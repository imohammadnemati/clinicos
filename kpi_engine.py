"""
KPI Engine – Daily performance metrics for clinics.
Calculates leads, appointments, revenue, conversion rates, top objections, etc.
No LLM dependencies, only database queries.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import Counter
from database import SessionLocal
from models import DailyKPI, Lead, Appointment, RawMessage, Patient, ObjectionLog, ServicePrice
import json
import logging

logger = logging.getLogger(__name__)


def calculate_daily_kpi(clinic_id: int, date: datetime) -> Optional[Dict]:
    """
    Calculate and store daily KPIs for a given clinic and date.
    Returns a dictionary with the calculated metrics, or None on error.
    """
    db = SessionLocal()
    try:
        start = datetime(date.year, date.month, date.day)
        end = start + timedelta(days=1)

        # ----- Basic counts -----
        messages_count = db.query(RawMessage).filter(
            RawMessage.clinic_id == clinic_id,
            RawMessage.created_at >= start,
            RawMessage.created_at < end
        ).count()

        leads_count = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.created_at >= start,
            Lead.created_at < end
        ).count()

        booked_count = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.pipeline_stage == 'booked',
            Lead.created_at >= start,
            Lead.created_at < end
        ).count()

        completed_count = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id,
            Appointment.status == 'completed',
            Appointment.appointment_date >= start,
            Appointment.appointment_date < end
        ).count()

        lost_count = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.pipeline_stage == 'lost',
            Lead.created_at >= start,
            Lead.created_at < end
        ).count()

        no_show_count = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id,
            Appointment.status == 'no_show',
            Appointment.appointment_date >= start,
            Appointment.appointment_date < end
        ).count()

        # ----- Revenue -----
        completed_appointments = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id,
            Appointment.status == 'completed',
            Appointment.appointment_date >= start,
            Appointment.appointment_date < end,
            Appointment.revenue.isnot(None)
        ).all()
        revenue = sum(a.revenue or 0 for a in completed_appointments)

        # ----- Conversion rate -----
        conversion_rate = (booked_count / leads_count * 100) if leads_count > 0 else 0

        # ----- Top objections -----
        objections = db.query(Lead.objection_category).filter(
            Lead.clinic_id == clinic_id,
            Lead.created_at >= start,
            Lead.created_at < end,
            Lead.objection_category.isnot(None),
            Lead.objection_category != 'none'
        ).all()
        objection_counts = Counter([obj[0] for obj in objections if obj[0]])
        top_objections = [
            {"category": cat, "count": count}
            for cat, count in objection_counts.most_common(5)
        ]

        # ----- Top services -----
        services = db.query(Lead.service).filter(
            Lead.clinic_id == clinic_id,
            Lead.created_at >= start,
            Lead.created_at < end,
            Lead.service.isnot(None),
            Lead.service != 'none'
        ).all()
        service_counts = Counter([s[0] for s in services if s[0]])
        top_services = [
            {"service": srv, "count": count}
            for srv, count in service_counts.most_common(5)
        ]

        # ----- Lost revenue estimate -----
        # Get average service prices
        price_map = {}
        prices = db.query(ServicePrice).filter(
            ServicePrice.clinic_id == clinic_id,
            ServicePrice.effective_date <= end
        ).all()
        for sp in prices:
            price_map[sp.service] = sp.price

        lost_revenue = 0
        lost_leads = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.pipeline_stage == 'lost',
            Lead.created_at >= start,
            Lead.created_at < end
        ).all()
        for lead in lost_leads:
            service = lead.service
            if service and service in price_map:
                # Estimate 30% conversion rate loss
                lost_revenue += price_map[service] * 0.3

        # ----- Update or insert KPI record -----
        existing = db.query(DailyKPI).filter_by(clinic_id=clinic_id, date=start).first()
        top_obj_json = json.dumps(top_objections, ensure_ascii=False)
        top_serv_json = json.dumps(top_services, ensure_ascii=False)

        if existing:
            existing.messages_count = messages_count
            existing.leads_count = leads_count
            existing.booked_count = booked_count
            existing.completed_count = completed_count
            existing.lost_count = lost_count
            existing.no_show_count = no_show_count
            existing.revenue = revenue
            existing.lost_revenue = lost_revenue
            existing.top_objections = top_obj_json
            existing.top_services = top_serv_json
            existing.conversion_rate = conversion_rate
        else:
            kpi = DailyKPI(
                clinic_id=clinic_id,
                date=start,
                messages_count=messages_count,
                leads_count=leads_count,
                booked_count=booked_count,
                completed_count=completed_count,
                lost_count=lost_count,
                no_show_count=no_show_count,
                revenue=revenue,
                lost_revenue=lost_revenue,
                top_objections=top_obj_json,
                top_services=top_serv_json,
                conversion_rate=conversion_rate,
                created_at=datetime.utcnow()
            )
            db.add(kpi)

        db.commit()
        result = {
            "messages_count": messages_count,
            "leads_count": leads_count,
            "booked_count": booked_count,
            "completed_count": completed_count,
            "lost_count": lost_count,
            "no_show_count": no_show_count,
            "revenue": revenue,
            "lost_revenue": lost_revenue,
            "conversion_rate": conversion_rate,
            "top_objections": top_objections,
            "top_services": top_services
        }
        return result
    except Exception as e:
        logger.error(f"Error calculating KPI for clinic {clinic_id} on {date}: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def get_weekly_kpi(clinic_id: int, end_date: Optional[datetime] = None) -> List[Dict]:
    """Return KPI records for the last 7 days."""
    if end_date is None:
        end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    db = SessionLocal()
    try:
        kpis = db.query(DailyKPI).filter(
            DailyKPI.clinic_id == clinic_id,
            DailyKPI.date >= start_date,
            DailyKPI.date <= end_date
        ).order_by(DailyKPI.date).all()
        return [
            {
                "date": k.date.strftime("%Y-%m-%d"),
                "leads": k.leads_count,
                "booked": k.booked_count,
                "completed": k.completed_count,
                "conversion_rate": round(k.conversion_rate, 2),
                "revenue": k.revenue,
                "lost_revenue": k.lost_revenue
            }
            for k in kpis
        ]
    finally:
        db.close()


def get_monthly_kpi(clinic_id: int, year: int, month: int) -> Dict:
    """Aggregate KPI for a whole month."""
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    db = SessionLocal()
    try:
        kpis = db.query(DailyKPI).filter(
            DailyKPI.clinic_id == clinic_id,
            DailyKPI.date >= start_date,
            DailyKPI.date < end_date
        ).all()

        total_leads = sum(k.leads_count for k in kpis)
        total_booked = sum(k.booked_count for k in kpis)
        total_completed = sum(k.completed_count for k in kpis)
        total_revenue = sum(k.revenue or 0 for k in kpis)
        total_lost_revenue = sum(k.lost_revenue or 0 for k in kpis)

        # Aggregate top objections across month
        all_objs = []
        for k in kpis:
            if k.top_objections:
                objs = json.loads(k.top_objections)
                all_objs.extend(objs)
        obj_counter = Counter()
        for obj in all_objs:
            obj_counter[obj.get('category', 'unknown')] += obj.get('count', 1)

        # Aggregate top services
        all_serv = []
        for k in kpis:
            if k.top_services:
                serv = json.loads(k.top_services)
                all_serv.extend(serv)
        serv_counter = Counter()
        for s in all_serv:
            serv_counter[s.get('service', 'unknown')] += s.get('count', 1)

        return {
            "year": year,
            "month": month,
            "total_leads": total_leads,
            "total_booked": total_booked,
            "total_completed": total_completed,
            "total_revenue": total_revenue,
            "total_lost_revenue": total_lost_revenue,
            "overall_conversion_rate": round((total_booked / total_leads * 100) if total_leads > 0 else 0, 2),
            "top_objections": [
                {"category": cat, "count": count}
                for cat, count in obj_counter.most_common(5)
            ],
            "top_services": [
                {"service": srv, "count": count}
                for srv, count in serv_counter.most_common(5)
            ]
        }
    finally:
        db.close()


def get_kpi_summary(clinic_id: int) -> Dict:
    """Return a summary for today, last week, last month."""
    db = SessionLocal()
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    try:
        today = db.query(DailyKPI).filter_by(clinic_id=clinic_id, date=today_start).first()
        weekly = db.query(DailyKPI).filter(DailyKPI.date >= week_ago).all()
        monthly = db.query(DailyKPI).filter(DailyKPI.date >= month_ago).all()

        weekly_leads = sum(k.leads_count for k in weekly)
        weekly_booked = sum(k.booked_count for k in weekly)
        weekly_conversion = (weekly_booked / weekly_leads * 100) if weekly_leads > 0 else 0

        monthly_leads = sum(k.leads_count for k in monthly)
        monthly_booked = sum(k.booked_count for k in monthly)
        monthly_conversion = (monthly_booked / monthly_leads * 100) if monthly_leads > 0 else 0

        # Trend: compare this week to previous week
        two_weeks_ago = now - timedelta(days=14)
        prev_week = db.query(DailyKPI).filter(
            DailyKPI.date >= two_weeks_ago,
            DailyKPI.date < week_ago
        ).all()
        prev_week_leads = sum(k.leads_count for k in prev_week)
        leads_trend = ((weekly_leads - prev_week_leads) / prev_week_leads * 100) if prev_week_leads > 0 else 0

        return {
            "today": {
                "leads": today.leads_count if today else 0,
                "booked": today.booked_count if today else 0,
                "completed": today.completed_count if today else 0,
                "revenue": today.revenue if today else 0
            },
            "weekly": {
                "leads": weekly_leads,
                "booked": weekly_booked,
                "conversion_rate": round(weekly_conversion, 2),
                "leads_trend": round(leads_trend, 1)
            },
            "monthly": {
                "leads": monthly_leads,
                "booked": monthly_booked,
                "conversion_rate": round(monthly_conversion, 2)
            }
        }
    finally:
        db.close()


def get_staff_performance(clinic_id: int, days: int = 30) -> List[Dict]:
    """Return performance stats for staff members (leads handled, appointments confirmed, etc.)."""
    db = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=days)
    try:
        from models import Staff
        staff_members = db.query(Staff).filter(Staff.clinic_id == clinic_id).all()
        result = []
        for staff in staff_members:
            # Count leads created by this staff (if created_by column exists, else skip)
            # In current schema, Lead has no direct staff link, so we return basic info.
            result.append({
                "staff_id": staff.id,
                "name": staff.name,
                "role": staff.role,
                "telegram_id": staff.telegram_id,
                "joined_days": (datetime.utcnow() - staff.created_at).days
            })
        return result
    finally:
        db.close()


def export_kpi_to_json(clinic_id: int, start_date: datetime, end_date: datetime) -> str:
    """Export KPI data as JSON string for the given period."""
    db = SessionLocal()
    try:
        kpis = db.query(DailyKPI).filter(
            DailyKPI.clinic_id == clinic_id,
            DailyKPI.date >= start_date,
            DailyKPI.date <= end_date
        ).order_by(DailyKPI.date).all()
        export_data = []
        for k in kpis:
            export_data.append({
                "date": k.date.isoformat(),
                "messages_count": k.messages_count,
                "leads_count": k.leads_count,
                "booked_count": k.booked_count,
                "completed_count": k.completed_count,
                "lost_count": k.lost_count,
                "no_show_count": k.no_show_count,
                "revenue": k.revenue,
                "lost_revenue": k.lost_revenue,
                "conversion_rate": k.conversion_rate,
                "top_objections": json.loads(k.top_objections) if k.top_objections else [],
                "top_services": json.loads(k.top_services) if k.top_services else []
            })
        return json.dumps(export_data, ensure_ascii=False, indent=2)
    finally:
        db.close()