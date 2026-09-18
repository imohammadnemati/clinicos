"""
Session Manager – Manages conversation sessions between patients and the bot.
Handles session creation, activity tracking, session closure, and status queries.
No LLM dependencies.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from database import SessionLocal
from models import Session
from config import SESSION_HOURS
import logging

logger = logging.getLogger(__name__)


def get_or_create_session(clinic_id: int, patient_id: int) -> int:
    """
    Retrieve an active session for the patient, or create a new one.
    A session is considered active if its last_activity is within SESSION_HOURS.
    Returns the session ID.
    """
    db = SessionLocal()
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=SESSION_HOURS)

    try:
        # Try to find an active session (based on last_activity)
        active = db.query(Session).filter(
            Session.clinic_id == clinic_id,
            Session.patient_id == patient_id,
            Session.is_active == True,
            Session.last_activity > cutoff
        ).first()

        if active:
            # Update last_activity to now
            active.last_activity = now
            db.commit()
            logger.debug(f"Active session found for patient {patient_id}: {active.id}")
            return active.id

        # Close any old sessions that are still marked active
        db.query(Session).filter(
            Session.clinic_id == clinic_id,
            Session.patient_id == patient_id,
            Session.is_active == True
        )
        if clinic_id is not None:
            query = query.filter(Session.clinic_id == clinic_id)
        result = query.update({"is_active": False, "end_time": now})

        # Create new session
        new_session = Session(
            clinic_id=clinic_id,
            patient_id=patient_id,
            start_time=now,
            last_activity=now,
            is_active=True,
            requires_human=False,
            conversation_status='active'
        )
        db.add(new_session)
        db.commit()
        session_id = new_session.id
        logger.info(f"New session created for patient {patient_id}: {session_id}")
        return session_id
    except Exception as e:
        logger.error(f"Error in get_or_create_session for patient {patient_id}: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def update_session_activity(session_id: int, clinic_id: Optional[int] = None) -> bool:
    """
    Update the last_activity timestamp of a session.
    Returns True if successful, False otherwise.
    """
    db = SessionLocal()
    try:
        query = db.query(Session).filter(Session.id == session_id)
        if clinic_id is not None:
            query = query.filter(Session.clinic_id == clinic_id)
        session = query.first()
        if session:
            session.last_activity = datetime.utcnow()
            db.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating activity for session {session_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def close_session(session_id: int, clinic_id: Optional[int] = None) -> bool:
    """
    Close a session (set is_active=False, record end_time).
    Returns True on success.
    """
    db = SessionLocal()
    now = datetime.utcnow()
    try:
        query = db.query(Session).filter(Session.id == session_id)
        if clinic_id is not None:
            query = query.filter(Session.clinic_id == clinic_id)
        result = query.update({
            "is_active": False,
            "end_time": now
        })
        db.commit()
        if result:
            logger.info(f"Session {session_id} closed.")
            return True
        logger.warning(f"Session {session_id} not found.")
        return False
    except Exception as e:
        logger.error(f"Error closing session {session_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def set_session_requires_human(
    session_id: int, requires_human: bool = True, clinic_id: Optional[int] = None
) -> bool:
    """
    Mark a session as needing human intervention.
    """
    db = SessionLocal()
    try:
        query = db.query(Session).filter(Session.id == session_id)
        if clinic_id is not None:
            query = query.filter(Session.clinic_id == clinic_id)
        result = query.update({
            "requires_human": requires_human,
            "conversation_status": "human_required" if requires_human else "active"
        })
        db.commit()
        return result > 0
    except Exception as e:
        logger.error(f"Error setting human flag on session {session_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def get_session_conversation_state(
    session_id: int, clinic_id: Optional[int] = None
) -> Optional[Dict]:
    """
    Retrieve the conversation state of a session (for debugging and UI).
    """
    db = SessionLocal()
    try:
        query = db.query(Session).filter(Session.id == session_id)
        if clinic_id is not None:
            query = query.filter(Session.clinic_id == clinic_id)
        session = query.first()
        if not session:
            return None
        return {
            "id": session.id,
            "patient_id": session.patient_id,
            "start_time": session.start_time,
            "is_active": session.is_active,
            "requires_human": session.requires_human,
            "conversation_status": session.conversation_status,
            "last_activity": session.last_activity
        }
    except Exception as e:
        logger.error(f"Error retrieving session state {session_id}: {e}")
        return None
    finally:
        db.close()


def is_session_active(session_id: int, clinic_id: Optional[int] = None) -> bool:
    """
    Check if a session is still considered active (based on last_activity).
    """
    db = SessionLocal()
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=SESSION_HOURS)
    try:
        query = db.query(Session).filter(
            Session.id == session_id,
            Session.is_active == True,
            Session.last_activity > cutoff
        )
        if clinic_id is not None:
            query = query.filter(Session.clinic_id == clinic_id)
        session = query.first()
        return session is not None
    except Exception as e:
        logger.error(f"Error checking active status for session {session_id}: {e}")
        return False
    finally:
        db.close()


def close_all_patient_sessions(patient_id: int, clinic_id: Optional[int] = None) -> int:
    """
    Close all active sessions belonging to a patient.
    Returns the number of sessions closed.
    """
    db = SessionLocal()
    now = datetime.utcnow()
    try:
        query = db.query(Session).filter(
            Session.patient_id == patient_id,

            Session.is_active == True
        ).update({
            "is_active": False,
            "end_time": now
        })
        db.commit()
        if result:
            logger.info(f"Closed {result} sessions for patient {patient_id}.")
        return result
    except Exception as e:
        logger.error(f"Error closing sessions for patient {patient_id}: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def get_patient_session_history(
    patient_id: int, limit: int = 10, clinic_id: Optional[int] = None
) -> List[Dict]:
    """
    Return a list of the last `limit` sessions for a patient.
    """
    db = SessionLocal()
    try:
        query = db.query(Session).filter(Session.patient_id == patient_id)
        if clinic_id is not None:
            query = query.filter(Session.clinic_id == clinic_id)
        sessions = query.order_by(Session.start_time.desc()).limit(limit).all()
        return [
            {
                "id": s.id,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "is_active": s.is_active,
                "requires_human": s.requires_human
            }
            for s in sessions
        ]
    except Exception as e:
        logger.error(f"Error fetching session history for patient {patient_id}: {e}")
        return []
    finally:
        db.close()


def get_active_sessions_count(clinic_id: int) -> int:
    """
    Count active sessions for a clinic (used for monitoring).
    """
    db = SessionLocal()
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=SESSION_HOURS)
    try:
        count = db.query(Session).filter(
            Session.clinic_id == clinic_id,
            Session.is_active == True,
            Session.last_activity > cutoff
        ).count()
        return count
    except Exception as e:
        logger.error(f"Error counting active sessions for clinic {clinic_id}: {e}")
        return 0
    finally:
        db.close()


def format_session_duration(session: Session) -> str:
    """
    Format the duration of a session for display (human readable).
    """
    if not session.end_time:
        end = datetime.utcnow()
    else:
        end = session.end_time
    duration = end - session.start_time
    minutes = int(duration.total_seconds() // 60)
    if minutes < 60:
        return f"{minutes} minutes"
    else:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours} hours and {mins} minutes"