"""
ماژول موتور شاخص‌های کلیدی عملکرد (KPI Engine)
این ماژول مسئول محاسبه و ذخیره شاخص‌های کلیدی عملکرد برای هر کلینیک است:
- تعداد پیام‌ها، لیدها، نوبت‌ها
- نرخ تبدیل (Conversion Rate)
- درآمد و درآمد از دست رفته
- اعتراضات برتر و خدمات برتر
- آمار عملکرد منشی و پزشکان
- روندهای هفتگی و ماهانه
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter
from database import SessionLocal
from models import (
    DailyKPI, Lead, Appointment, Event, RawMessage, 
    Staff, Clinic, ServicePrice, ObjectionLog
)
import json
import logging

# تنظیم لاگر
logger = logging.getLogger(__name__)


def calculate_daily_kpi(clinic_id: int, date: datetime) -> Optional[Dict]:
    """
    محاسبه شاخص‌های کلیدی عملکرد برای یک روز مشخص
    پارامترها:
        clinic_id: شناسه کلینیک
        date: تاریخ مورد نظر
    خروجی:
        دیکشنری آمار یا None در صورت خطا
    """
    db = SessionLocal()
    try:
        start = datetime(date.year, date.month, date.day)
        end = start + timedelta(days=1)
        
        logger.info(f"محاسبه KPI برای کلینیک {clinic_id} در تاریخ {start.date()}")
        
        # ========== آمار پایه ==========
        # تعداد پیام‌ها
        messages_count = db.query(RawMessage).filter(
            RawMessage.clinic_id == clinic_id,
            RawMessage.created_at >= start,
            RawMessage.created_at < end
        ).count()
        
        # تعداد لیدهای جدید
        leads_count = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.created_at >= start,
            Lead.created_at < end
        ).count()
        
        # تعداد نوبت‌های رزرو شده در این روز
        booked_count = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.pipeline_stage == 'booked',
            Lead.created_at >= start,
            Lead.created_at < end
        ).count()
        
        # تعداد نوبت‌های انجام شده در این روز
        completed_count = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id,
            Appointment.status == 'completed',
            Appointment.appointment_date >= start,
            Appointment.appointment_date < end
        ).count()
        
        # تعداد لیدهای از دست رفته
        lost_count = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.pipeline_stage == 'lost',
            Lead.created_at >= start,
            Lead.created_at < end
        ).count()
        
        # تعداد عدم حضور (No-Show)
        no_show_count = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id,
            Appointment.status == 'no_show',
            Appointment.appointment_date >= start,
            Appointment.appointment_date < end
        ).count()
        
        # ========== درآمد ==========
        # درآمد واقعی از نوبت‌های تکمیل شده
        completed_appointments = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id,
            Appointment.status == 'completed',
            Appointment.appointment_date >= start,
            Appointment.appointment_date < end,
            Appointment.revenue.isnot(None)
        ).all()
        
        revenue = sum(a.revenue or 0 for a in completed_appointments)
        
        # ========== نرخ تبدیل ==========
        conversion_rate = (booked_count / leads_count * 100) if leads_count > 0 else 0
        
        # ========== اعتراضات برتر ==========
        # از جدول ObjectionLog
        objection_logs = db.query(ObjectionLog).join(
            Event, ObjectionLog.event_id == Event.id
        ).filter(
            Event.clinic_id == clinic_id,
            Event.created_at >= start,
            Event.created_at < end
        ).all()
        
        objection_counter = Counter([obj.category for obj in objection_logs if obj.category])
        
        # همچنین از Lead.objection_category
        leads_with_obj = db.query(Lead.objection_category).filter(
            Lead.clinic_id == clinic_id,
            Lead.created_at >= start,
            Lead.created_at < end,
            Lead.objection_category.isnot(None),
            Lead.objection_category != 'none'
        ).all()
        
        for obj in leads_with_obj:
            if obj[0]:
                objection_counter[obj[0]] += 1
        
        top_objections = [
            {"category": cat, "count": count}
            for cat, count in objection_counter.most_common(5)
        ]
        
        # ========== خدمات برتر ==========
        services = db.query(Lead.service).filter(
            Lead.clinic_id == clinic_id,
            Lead.created_at >= start,
            Lead.created_at < end,
            Lead.service.isnot(None),
            Lead.service != 'none'
        ).all()
        
        service_counter = Counter([srv[0] for srv in services if srv[0]])
        top_services = [
            {"service": srv, "count": count}
            for srv, count in service_counter.most_common(5)
        ]
        
        # ========== درآمد از دست رفته (تخمینی) ==========
        # دریافت قیمت متوسط خدمات
        service_prices = db.query(ServicePrice).filter(
            ServicePrice.clinic_id == clinic_id,
            ServicePrice.effective_date <= end
        ).all()
        
        price_map = {}
        for sp in service_prices:
            price_map[sp.service] = sp.price
        
        # محاسبه درآمد از دست رفته از لیدهای lost
        lost_leads = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.pipeline_stage == 'lost',
            Lead.created_at >= start,
            Lead.created_at < end
        ).all()
        
        lost_revenue = 0
        for lead in lost_leads:
            service = lead.service
            if service and service in price_map:
                # فرض می‌کنیم 30% نرخ تبدیل معمولی
                lost_revenue += price_map[service] * 0.3
        
        # ========== آمار تعامل ==========
        # میانگین زمان پاسخ (ساده شده)
        # (در نسخه کامل باید زمان بین پیام بیمار و پاسخ ربات محاسبه شود)
        
        # ========== آمار عملکرد کارکنان ==========
        staff_stats = []
        staff_members = db.query(Staff).filter(
            Staff.clinic_id == clinic_id,
            Staff.role.in_(['doctor', 'secretary'])
        ).all()
        
        for staff in staff_members:
            # تعداد لیدهای مربوط به این کارمند
            staff_leads = db.query(Lead).filter(
                Lead.clinic_id == clinic_id,
                Lead.created_at >= start,
                Lead.created_at < end
            ).count()
            staff_stats.append({
                "staff_id": staff.id,
                "name": staff.name,
                "role": staff.role,
                "leads_handled": staff_leads
            })
        
        # ========== ایجاد یا به‌روزرسانی رکورد KPI ==========
        existing_kpi = db.query(DailyKPI).filter_by(
            clinic_id=clinic_id,
            date=start
        ).first()
        
        top_obj_json = json.dumps(top_objections, ensure_ascii=False)
        top_serv_json = json.dumps(top_services, ensure_ascii=False)
        
        if existing_kpi:
            existing_kpi.messages_count = messages_count
            existing_kpi.leads_count = leads_count
            existing_kpi.booked_count = booked_count
            existing_kpi.completed_count = completed_count
            existing_kpi.lost_count = lost_count
            existing_kpi.no_show_count = no_show_count
            existing_kpi.revenue = revenue
            existing_kpi.lost_revenue = lost_revenue
            existing_kpi.top_objections = top_obj_json
            existing_kpi.top_services = top_serv_json
            existing_kpi.conversion_rate = conversion_rate
            existing_kpi.updated_at = datetime.utcnow()
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
            "top_services": top_services,
            "staff_stats": staff_stats
        }
        
        logger.info(f"KPI برای کلینیک {clinic_id} در تاریخ {start.date()} محاسبه شد.")
        return result
        
    except Exception as e:
        logger.error(f"خطا در محاسبه KPI برای کلینیک {clinic_id}: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def get_weekly_kpi(clinic_id: int, end_date: Optional[datetime] = None) -> List[Dict]:
    """
    دریافت KPI هفتگی (۷ روز گذشته)
    """
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
        
        result = []
        for kpi in kpis:
            result.append({
                "date": kpi.date.strftime("%Y-%m-%d"),
                "leads": kpi.leads_count,
                "booked": kpi.booked_count,
                "completed": kpi.completed_count,
                "conversion_rate": round(kpi.conversion_rate, 2),
                "revenue": kpi.revenue,
                "lost_revenue": kpi.lost_revenue
            })
        
        return result
    finally:
        db.close()


def get_monthly_kpi(clinic_id: int, year: int, month: int) -> Dict:
    """
    دریافت KPI ماهانه
    """
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
        
        # جمع‌آوری اعتراضات ماهانه
        all_objections = []
        for kpi in kpis:
            if kpi.top_objections:
                objections = json.loads(kpi.top_objections)
                all_objections.extend(objections)
        
        objection_counter = Counter()
        for obj in all_objections:
            objection_counter[obj.get('category', 'unknown')] += obj.get('count', 1)
        
        # جمع‌آوری خدمات ماهانه
        all_services = []
        for kpi in kpis:
            if kpi.top_services:
                services = json.loads(kpi.top_services)
                all_services.extend(services)
        
        service_counter = Counter()
        for srv in all_services:
            service_counter[srv.get('service', 'unknown')] += srv.get('count', 1)
        
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
                for cat, count in objection_counter.most_common(5)
            ],
            "top_services": [
                {"service": srv, "count": count}
                for srv, count in service_counter.most_common(5)
            ]
        }
    finally:
        db.close()


def get_kpi_summary(clinic_id: int) -> Dict:
    """
    دریافت خلاصه KPI برای داشبورد اصلی
    """
    db = SessionLocal()
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    try:
        # امروز
        today_kpi = db.query(DailyKPI).filter_by(
            clinic_id=clinic_id, 
            date=today_start
        ).first()
        
        # هفته گذشته
        weekly_kpis = db.query(DailyKPI).filter(
            DailyKPI.clinic_id == clinic_id,
            DailyKPI.date >= week_ago
        ).all()
        
        # ماه گذشته
        monthly_kpis = db.query(DailyKPI).filter(
            DailyKPI.clinic_id == clinic_id,
            DailyKPI.date >= month_ago
        ).all()
        
        # جمع‌آوری آمار هفتگی
        weekly_leads = sum(k.leads_count for k in weekly_kpis)
        weekly_booked = sum(k.booked_count for k in weekly_kpis)
        weekly_conversion = (weekly_booked / weekly_leads * 100) if weekly_leads > 0 else 0
        
        # جمع‌آوری آمار ماهانه
        monthly_leads = sum(k.leads_count for k in monthly_kpis)
        monthly_booked = sum(k.booked_count for k in monthly_kpis)
        monthly_conversion = (monthly_booked / monthly_leads * 100) if monthly_leads > 0 else 0
        
        # روند تغییرات (مقایسه هفته جاری با هفته قبل)
        two_weeks_ago = now - timedelta(days=14)
        prev_week_kpis = db.query(DailyKPI).filter(
            DailyKPI.clinic_id == clinic_id,
            DailyKPI.date >= two_weeks_ago,
            DailyKPI.date < week_ago
        ).all()
        
        prev_week_leads = sum(k.leads_count for k in prev_week_kpis)
        leads_trend = ((weekly_leads - prev_week_leads) / prev_week_leads * 100) if prev_week_leads > 0 else 0
        
        return {
            "today": {
                "leads": today_kpi.leads_count if today_kpi else 0,
                "booked": today_kpi.booked_count if today_kpi else 0,
                "completed": today_kpi.completed_count if today_kpi else 0,
                "revenue": today_kpi.revenue if today_kpi else 0
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
    """
    دریافت آمار عملکرد کارکنان (منشی‌ها و پزشکان)
    """
    db = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    try:
        staff_members = db.query(Staff).filter(
            Staff.clinic_id == clinic_id,
            Staff.role.in_(['doctor', 'secretary'])
        ).all()
        
        performance = []
        for staff in staff_members:
            # تعداد لیدهای ثبت شده توسط این کارمند
            # (در صورت وجود فیلد created_by در Lead)
            leads_count = db.query(Lead).filter(
                Lead.clinic_id == clinic_id,
                Lead.created_at >= cutoff
            ).count()
            
            # تعداد نوبت‌های تأیید شده توسط این کارمند
            appointments_count = db.query(Appointment).filter(
                Appointment.clinic_id == clinic_id,
                Appointment.created_at >= cutoff
            ).count()
            
            performance.append({
                "staff_id": staff.id,
                "name": staff.name,
                "role": staff.role,
                "leads_handled": leads_count,
                "appointments_confirmed": appointments_count,
                "telegram_id": staff.telegram_id,
                "joined_days": (datetime.utcnow() - staff.created_at).days
            })
        
        return performance
    finally:
        db.close()


def export_kpi_to_json(clinic_id: int, start_date: datetime, end_date: datetime) -> str:
    """
    خروجی KPI به فرمت JSON برای دانلود
    """
    db = SessionLocal()
    
    try:
        kpis = db.query(DailyKPI).filter(
            DailyKPI.clinic_id == clinic_id,
            DailyKPI.date >= start_date,
            DailyKPI.date <= end_date
        ).order_by(DailyKPI.date).all()
        
        result = []
        for kpi in kpis:
            result.append({
                "date": kpi.date.isoformat(),
                "messages_count": kpi.messages_count,
                "leads_count": kpi.leads_count,
                "booked_count": kpi.booked_count,
                "completed_count": kpi.completed_count,
                "lost_count": kpi.lost_count,
                "no_show_count": kpi.no_show_count,
                "revenue": kpi.revenue,
                "lost_revenue": kpi.lost_revenue,
                "conversion_rate": kpi.conversion_rate,
                "top_objections": json.loads(kpi.top_objections) if kpi.top_objections else [],
                "top_services": json.loads(kpi.top_services) if kpi.top_services else []
            })
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    finally:
        db.close()


def get_conversion_funnel(clinic_id: int, days: int = 30) -> Dict:
    """
    دریافت قیف تبدیل (Conversion Funnel) برای یک دوره مشخص
    """
    db = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    try:
        # مرحله 1: پیام‌های دریافتی
        messages = db.query(RawMessage).filter(
            RawMessage.clinic_id == clinic_id,
            RawMessage.created_at >= cutoff
        ).count()
        
        # مرحله 2: لیدهای ایجاد شده
        leads = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.created_at >= cutoff
        ).count()
        
        # مرحله 3: مشاوره (درخواست نوبت)
        consultations = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.pipeline_stage == 'consultation',
            Lead.created_at >= cutoff
        ).count()
        
        # مرحله 4: نوبت‌های رزرو شده
        booked = db.query(Lead).filter(
            Lead.clinic_id == clinic_id,
            Lead.pipeline_stage == 'booked',
            Lead.created_at >= cutoff
        ).count()
        
        # مرحله 5: نوبت‌های تکمیل شده
        completed = db.query(Appointment).filter(
            Appointment.clinic_id == clinic_id,
            Appointment.status == 'completed',
            Appointment.appointment_date >= cutoff
        ).count()
        
        return {
            "period_days": days,
            "messages": messages,
            "leads": leads,
            "consultations": consultations,
            "booked": booked,
            "completed": completed,
            "message_to_lead_rate": round((leads / messages * 100) if messages > 0 else 0, 2),
            "lead_to_booked_rate": round((booked / leads * 100) if leads > 0 else 0, 2),
            "booked_to_completed_rate": round((completed / booked * 100) if booked > 0 else 0, 2),
            "overall_rate": round((completed / messages * 100) if messages > 0 else 0, 2)
        }
    finally:
        db.close()