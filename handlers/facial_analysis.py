# handlers/facial_analysis.py
import os
import tempfile
import logging
import asyncio
import json
import re
from datetime import datetime
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy.orm import Session

from config import (
    FACIAL_ANALYSIS_TIMEOUT,
    MAX_PATIENT_FACIAL_ANALYSES,
    PDF_REPORT_ENABLED,
    PDF_REPORT_FONT_PATH
)
from database import SessionLocal
from models import (
    Patient,
    Staff,
    PatientAlias,
    FacialAnalysis,
    FacialLandmarks,
    FacialMetrics,
    TreatmentRecommendation,
    FacialAnalysisUsage,
    KnowledgeItem,
    Clinic
)
from utils.image_quality import check_image_quality
from utils.facial_metrics import compute_facial_metrics
from services.pdf_generator import generate_facial_report
from utils.role_utils import get_user_role, get_user_language, get_user_clinic_id
from patient_agent import _router, save_to_knowledge
from i18n import get_text


logger = logging.getLogger(__name__)

_PRESCRIPTIVE_QUANTITY_RE = re.compile(
    r"(?i)\\b\\d+(?:\\.\\d+)?\\s*(?:cc|ml|units?|mg|µg|mcg|iu)\\b"
)
_PRESCRIPTIVE_FIELD_NAMES = {
    "estimated_units", "estimated_volume", "dose", "dosage",
    "units", "volume", "quantity", "frequency",
}


def _sanitize_medical_output(value):
    """Recursively remove prescriptive quantities from untrusted LLM output."""
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if str(key).strip().lower() in _PRESCRIPTIVE_FIELD_NAMES:
                sanitized[key] = None
            else:
                sanitized[key] = _sanitize_medical_output(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_medical_output(item) for item in value]
    if isinstance(value, str) and _PRESCRIPTIVE_QUANTITY_RE.search(value):
        logger.warning("Medical safety gate blocked a prescriptive quantity.")
        return "Safety blocked: prescriptive dosing/quantity removed. Please consult a qualified clinician."
    return value


def _safe_analysis_data(raw):
    """Normalize only trusted schema fields from untrusted model output."""
    if not isinstance(raw, dict):
        return {
            "summary": "The facial analysis could not be safely parsed.",
            "recommendations": [],
            "disclaimer": "This analysis is informational only and does not replace an in-person clinical assessment.",
        }

    raw = _sanitize_medical_output(raw)
    recommendations = raw.get("recommendations", [])
    if not isinstance(recommendations, list):
        recommendations = []

    safe_recommendations = []
    for rec in recommendations:
        if not isinstance(rec, dict):
            continue
        safe_recommendations.append({
            "treatment_type": str(rec.get("treatment_type", ""))[:100],
            "area": str(rec.get("area", ""))[:100],
            "description": str(rec.get("description", ""))[:1000],
            "confidence": rec.get("confidence", None),
            "priority": rec.get("priority", None),
            "estimated_units": None,
            "estimated_volume": None,
            "price_estimate": None,
        })

    return {
        "summary": str(raw.get("summary", ""))[:2000],
        "recommendations": safe_recommendations,
        "disclaimer": "This analysis is informational only and does not replace an in-person clinical assessment.",
    }


def _build_safe_report_text(analysis_data):
    """Build persisted and delivered text only from sanitized structured data."""
    lines = [analysis_data.get("summary", "").strip()]
    for rec in analysis_data.get("recommendations", []):
        treatment = rec.get("treatment_type", "").strip()
        area = rec.get("area", "").strip()
        description = rec.get("description", "").strip()
        if treatment or area or description:
            lines.append(f"• {treatment} - {area}: {description}".strip())
    lines.append(analysis_data.get("disclaimer", "").strip())
    return "\n\n".join(line for line in lines if line)


# Conversation States
FACIAL_START = 30
FACIAL_INSTRUCTIONS = 31
FACIAL_GENDER = 32
FACIAL_AGE = 33
FACIAL_FRONT_PHOTO = 34
FACIAL_FRONT_CHECK = 35
FACIAL_RIGHT_PHOTO = 36
FACIAL_RIGHT_CHECK = 37
FACIAL_LEFT_PHOTO = 38
FACIAL_LEFT_CHECK = 39
FACIAL_ANALYZING = 40
FACIAL_RESULT = 41

async def facial_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start facial analysis flow with instructions."""
    user_id = update.effective_user.id
    role = get_user_role(user_id)
    lang = get_user_language(user_id) or 'fa'

    # Check usage limit only against the tenant-scoped patient identity.
    if role == 'patient':
        db = SessionLocal()
        try:
            clinic_id = get_user_clinic_id(user_id)
            if clinic_id is None:
                await update.message.reply_text(
                    "Clinic context could not be verified. Please register through your clinic link first."
                )
                return ConversationHandler.END

            patient = (
                db.query(Patient)
                .join(PatientAlias, PatientAlias.patient_id == Patient.id)
                .filter(
                    PatientAlias.platform == "telegram",
                    PatientAlias.external_user_id == str(user_id),
                    Patient.clinic_id == clinic_id,
                )
                .first()
            )
            if not patient:
                await update.message.reply_text(
                    "Patient not found. Please register with /start first."
                )
                return ConversationHandler.END

            usage = db.query(FacialAnalysisUsage).filter_by(patient_id=patient.id).first()
            if usage and usage.analysis_used:
                await update.message.reply_text(get_text("facial_limit_reached", lang))
                return ConversationHandler.END
        finally:
            db.close()

    instructions = get_text("facial_instructions", lang)
    keyboard = [
        [InlineKeyboardButton(get_text("facial_continue", lang), callback_data="facial_continue")],
        [InlineKeyboardButton(get_text("facial_cancel", lang), callback_data="facial_cancel")]
    ]
    await update.message.reply_text(instructions, reply_markup=InlineKeyboardMarkup(keyboard))
    return FACIAL_INSTRUCTIONS

async def facial_instructions_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = get_user_language(user_id) or 'fa'

    if query.data == "facial_cancel":
        await query.edit_message_text(get_text("facial_cancelled", lang))
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton(get_text("facial_gender_male", lang), callback_data="gender_male")],
        [InlineKeyboardButton(get_text("facial_gender_female", lang), callback_data="gender_female")],
        [InlineKeyboardButton(get_text("facial_gender_other", lang), callback_data="gender_other")]
    ]
    await query.edit_message_text(get_text("facial_ask_gender", lang), reply_markup=InlineKeyboardMarkup(keyboard))
    return FACIAL_GENDER

async def facial_gender_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    gender = query.data.split('_')[1]
    context.user_data['facial_gender'] = gender
    user_id = query.from_user.id
    lang = get_user_language(user_id) or 'fa'
    await query.edit_message_text(get_text("facial_ask_age", lang))
    return FACIAL_AGE

async def facial_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    lang = get_user_language(user_id) or 'fa'
    try:
        age = int(update.message.text.strip())
        if age < 1 or age > 120:
            raise ValueError
        context.user_data['facial_age'] = age
        await update.message.reply_text(get_text("facial_ask_front_photo", lang))
        return FACIAL_FRONT_PHOTO
    except ValueError:
        await update.message.reply_text(get_text("facial_invalid_age", lang))
        return FACIAL_AGE

async def facial_front_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_photo(update, context, "front")

async def facial_right_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_photo(update, context, "right")

async def facial_left_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_photo(update, context, "left")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, view: str) -> int:
    """Generic handler for photo uploads."""
    if not update.message.photo:
        user_id = update.effective_user.id
        lang = get_user_language(user_id) or 'fa'
        await update.message.reply_text(get_text("facial_send_photo", lang))
        return {'front': FACIAL_FRONT_PHOTO, 'right': FACIAL_RIGHT_PHOTO, 'left': FACIAL_LEFT_PHOTO}[view]

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp_path = tmp.name
    await file.download_to_drive(tmp_path)

    # Check quality
    is_valid, reason = check_image_quality(tmp_path)
    if not is_valid:
        os.unlink(tmp_path)
        user_id = update.effective_user.id
        lang = get_user_language(user_id) or 'fa'
        await update.message.reply_text(
            get_text("facial_quality_reject", lang).format(reason=reason)
        )
        return {'front': FACIAL_FRONT_PHOTO, 'right': FACIAL_RIGHT_PHOTO, 'left': FACIAL_LEFT_PHOTO}[view]

    # Store path
    context.user_data[f'facial_{view}_photo'] = tmp_path
    user_id = update.effective_user.id
    lang = get_user_language(user_id) or 'fa'
    await update.message.reply_text(get_text("facial_accept_photo", lang))

    # Determine next step
    if view == "front":
        await update.message.reply_text(get_text("facial_ask_right_photo", lang))
        return FACIAL_RIGHT_PHOTO
    elif view == "right":
        await update.message.reply_text(get_text("facial_ask_left_photo", lang))
        return FACIAL_LEFT_PHOTO
    else:  # left
        await update.message.reply_text(get_text("facial_analyzing", lang))
        # Start analysis
        await perform_facial_analysis(update, context)
        return ConversationHandler.END

async def perform_facial_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Core analysis logic."""
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        # Resolve tenant first; never use an unscoped Telegram alias lookup.
        clinic_id = get_user_clinic_id(user_id)
        if clinic_id is None:
            await update.message.reply_text(
                "Clinic context could not be verified. Please register through your clinic link first."
            )
            return

        patient = (
            db.query(Patient)
            .join(PatientAlias, PatientAlias.patient_id == Patient.id)
            .filter(
                PatientAlias.platform == "telegram",
                PatientAlias.external_user_id == str(user_id),
                Patient.clinic_id == clinic_id,
            )
            .first()
        )
        if not patient:
            await update.message.reply_text("Patient not found. Please register with /start first.")
            return

        # Get data from context
        front_path = context.user_data.get('facial_front_photo')
        right_path = context.user_data.get('facial_right_photo')
        left_path = context.user_data.get('facial_left_photo')
        gender = context.user_data.get('facial_gender', 'unknown')
        age = context.user_data.get('facial_age', 30)

        if not front_path or not os.path.exists(front_path):
            await update.message.reply_text("Front photo missing. Please try again.")
            return

        # Extract landmarks using MediaPipe
        import mediapipe as mp
        import cv2

        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)

        landmarks_data = {}
        for view, path in [('front', front_path), ('right', right_path), ('left', left_path)]:
            if path and os.path.exists(path):
                img = cv2.imread(path)
                if img is not None:
                    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    results = face_mesh.process(rgb)
                    if results.multi_face_landmarks:
                        h, w = img.shape[:2]
                        lm = results.multi_face_landmarks[0].landmark
                        points = [(int(l.x * w), int(l.y * h)) for l in lm]
                        landmarks_data[view] = points
        face_mesh.close()

        if not landmarks_data:
            await update.message.reply_text("Could not extract facial landmarks. Please try with better photos.")
            return

        # Compute metrics from front view
        metrics = compute_facial_metrics(landmarks_data.get('front', []))

        # Generate analysis using LLM
        # F-002: Prompt explicitly blocks dosages, units, and definitive prescriptions.
        analysis_prompt = f"""
        You are a medical aesthetics AI assistant. Analyze the following facial metrics and provide a professional aesthetic recommendation.
        Patient gender: {gender}, age: {age}
        Facial metrics (0-100 scale):
        - Overall Beauty: {metrics.get('overall_beauty', 0):.1f}
        - Symmetry: {metrics.get('eye_symmetry', 0):.1f}
        - Skin Quality: {metrics.get('skin_quality', 0):.1f}
        - Youthfulness: {metrics.get('youthfulness', 0):.1f}
        - Volume Balance: {metrics.get('volume_balance', 0):.1f}
        - Facial Harmony: {metrics.get('facial_harmony', 0):.1f}

        Provide recommendations (if any) for:
        1. Botox (forehead, glabellar, crow's feet, etc.)
        2. Filler (cheeks, nasolabial folds, lips, under-eye)
        3. Mesotherapy, PRP, skin boosters
        4. Other treatments

        Do not recommend specific dosages, units, or volumes. 
        Provide only aesthetic observations and general treatment categories. 
        Do not provide definitive medical prescriptions or patient-specific procedural quantities.

        Format the response as a JSON object with the following structure:
        {{
            "summary": "Brief summary of facial features",
            "recommendations": [
                {{
                    "treatment_type": "Botox",
                    "area": "Forehead",
                    "description": "Reduce forehead wrinkles",
                    "confidence": 0.85
                }}
            ],
            "disclaimer": "This analysis is for informational purposes only and does not replace a medical consultation."
        }}
        """

        analysis_data = {
            "summary": "Analysis could not be safely completed.",
            "recommendations": [],
            "disclaimer": "This analysis is informational only and does not replace an in-person clinical assessment.",
        }

        try:
            llm_response = await _router.generate(analysis_prompt, task="facial_analysis")
            try:
                parsed = json.loads(llm_response)
                analysis_data = _safe_analysis_data(parsed)
            except (TypeError, json.JSONDecodeError) as parse_e:
                logger.warning("Facial analysis JSON rejected: %s", parse_e)
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")

        report_text = _build_safe_report_text(analysis_data)

        # Save to database
        analysis = FacialAnalysis(
            patient_id=patient.id,
            clinic_id=patient.clinic_id,
            gender=gender,
            age=age,
            overall_beauty_score=metrics.get('overall_beauty', 0),
            symmetry_score=metrics.get('eye_symmetry', 0),
            skin_quality_score=metrics.get('skin_quality', 0),
            youthfulness_score=metrics.get('youthfulness', 0),
            volume_balance_score=metrics.get('volume_balance', 0),
            facial_harmony_score=metrics.get('facial_harmony', 0),
            estimated_apparent_age=age,
            report_text=report_text,
            status='completed'
        )
        db.add(analysis)
        db.flush()

        # Save landmarks
        for view, points in landmarks_data.items():
            lm = FacialLandmarks(
                analysis_id=analysis.id,
                view=view,
                landmarks=points,
                confidence=0.85
            )
            db.add(lm)

        # Save metrics
        for name, value in metrics.items():
            if isinstance(value, (int, float)):
                fm = FacialMetrics(
                    analysis_id=analysis.id,
                    metric_name=name,
                    value=float(value),
                    confidence=0.9,
                    category='general'
                )
                db.add(fm)

        # Save recommendations from analysis_data
        for rec in analysis_data.get('recommendations', []):
            tr = TreatmentRecommendation(
                analysis_id=analysis.id,
                treatment_type=rec.get('treatment_type', ''),
                area=rec.get('area', ''),
                estimated_units=None,
                estimated_volume=None,
                confidence=rec.get('confidence', 0.8),
                priority=rec.get('priority', 5),
                description=rec.get('description', ''),
                price_estimate=None
            )
            db.add(tr)

        # Record usage for patient
        role = get_user_role(user_id)
        if role == 'patient':
            usage = db.query(FacialAnalysisUsage).filter_by(patient_id=patient.id).first()
            if not usage:
                usage = FacialAnalysisUsage(patient_id=patient.id)
                db.add(usage)
            usage.analysis_used = True
            usage.used_at = datetime.utcnow()

        db.commit()

        # Generate PDF report
        pdf_path = None
        if PDF_REPORT_ENABLED:
            pdf_data = {
                'patient_name': patient.name,
                'gender': gender,
                'age': age,
                'overall_beauty': metrics.get('overall_beauty', 0),
                'symmetry': metrics.get('eye_symmetry', 0),
                'skin_quality': metrics.get('skin_quality', 0),
                'youthfulness': metrics.get('youthfulness', 0),
                'volume_balance': metrics.get('volume_balance', 0),
                'harmony': metrics.get('facial_harmony', 0),
                'recommendations': analysis_data.get('recommendations', []),
                'title': get_text("facial_report_title", get_user_language(user_id) or 'fa'),
            }
            pdf_path = generate_facial_report(pdf_data, language=get_user_language(user_id) or 'fa')
            if pdf_path and os.path.exists(pdf_path):
                analysis.report_pdf_url = pdf_path
                db.commit()

        # Send results
        lang = get_user_language(user_id) or 'fa'
        await update.message.reply_text(
            get_text("facial_result_summary", lang).format(
                overall=metrics.get('overall_beauty', 0),
                symmetry=metrics.get('eye_symmetry', 0),
                skin=metrics.get('skin_quality', 0),
                youth=metrics.get('youthfulness', 0),
                volume=metrics.get('volume_balance', 0),
                harmony=metrics.get('facial_harmony', 0)
            )
        )

        # Send PDF if available
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                await update.message.reply_document(f, filename='facial_analysis_report.pdf')
            os.unlink(pdf_path)
        else:
            # Send text report if PDF not available
            report_text = analysis_data.get('summary', '') + "\n\n"
            for rec in analysis_data.get('recommendations', []):
                report_text += f"• {rec.get('treatment_type')} - {rec.get('area')}: {rec.get('description')}\n"
            if report_text.strip():
                await update.message.reply_text(report_text[:3000])

        # Cleanup image files
        for path in [front_path, right_path, left_path]:
            if path and os.path.exists(path):
                os.unlink(path)

        # Save Q&A to knowledge base for future
        question = "چه خدماتی برای بهبود ظاهر صورت پیشنهاد می‌شود؟"  # generic
        answer = _build_safe_report_text(analysis_data)[:2000] if analysis_data else "تحلیل چهره انجام شد."
        await save_to_knowledge(patient.clinic_id, question, answer, db)

    except Exception as e:
        logger.error(f"Facial analysis error: {e}", exc_info=True)
        await update.message.reply_text("An error occurred during analysis. Please try again later.")
    finally:
        # Remove temporary uploaded images even when analysis fails midway.
        for path in (
            context.user_data.get('facial_front_photo'),
            context.user_data.get('facial_right_photo'),
            context.user_data.get('facial_left_photo'),
        ):
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except OSError:
                    logger.warning("Failed to remove temporary facial image: %s", path)
        db.close()
