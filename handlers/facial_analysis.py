# handlers/facial_analysis.py
import os
import tempfile
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy.orm import Session

from config import FACIAL_ANALYSIS_TIMEOUT, MAX_PATIENT_FACIAL_ANALYSES
from database import SessionLocal
from models import Patient, Staff, FacialAnalysis, FacialLandmarks, FacialMetrics, TreatmentRecommendation, FacialAnalysisUsage
from utils.image_quality import check_image_quality
from utils.facial_metrics import compute_facial_metrics
from services.pdf_generator import generate_facial_report
from patient_agent import _router
from i18n import get_text

logger = logging.getLogger(__name__)

# States
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
    db = SessionLocal()
    try:
        role = get_user_role(user_id, db)  # from bot.py helpers
        if role == 'patient':
            usage = db.query(FacialAnalysisUsage).filter_by(patient_id=user_id).first()
            if usage and usage.analysis_used:
                await update.message.reply_text(
                    get_text("facial_limit_reached", get_user_language(user_id, db))
                )
                return ConversationHandler.END
    finally:
        db.close()
    
    lang = get_user_language(user_id, db) or 'fa'
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
    if query.data == "facial_cancel":
        await query.edit_message_text(get_text("facial_cancelled", get_user_language(query.from_user.id, None)))
        return ConversationHandler.END
    
    lang = get_user_language(query.from_user.id, None) or 'fa'
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
    lang = get_user_language(query.from_user.id, None) or 'fa'
    await query.edit_message_text(get_text("facial_ask_age", lang))
    return FACIAL_AGE

async def facial_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        age = int(update.message.text.strip())
        if age < 1 or age > 120:
            raise ValueError
        context.user_data['facial_age'] = age
    except:
        await update.message.reply_text(get_text("facial_invalid_age", get_user_language(update.effective_user.id, None)))
        return FACIAL_AGE
    
    lang = get_user_language(update.effective_user.id, None) or 'fa'
    await update.message.reply_text(get_text("facial_ask_front_photo", lang))
    return FACIAL_FRONT_PHOTO

async def facial_front_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.photo:
        await update.message.reply_text(get_text("facial_send_photo", get_user_language(update.effective_user.id, None)))
        return FACIAL_FRONT_PHOTO
    
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp_path = tmp.name
    await file.download_to_drive(tmp_path)
    
    # Check quality
    is_valid, reason = check_image_quality(tmp_path)
    if not is_valid:
        os.unlink(tmp_path)
        lang = get_user_language(update.effective_user.id, None) or 'fa'
        await update.message.reply_text(
            get_text("facial_quality_reject", lang).format(reason=reason)
        )
        return FACIAL_FRONT_PHOTO
    
    context.user_data['facial_front_photo'] = tmp_path
    lang = get_user_language(update.effective_user.id, None) or 'fa'
    await update.message.reply_text(get_text("facial_accept_photo", lang))
    await update.message.reply_text(get_text("facial_ask_right_photo", lang))
    return FACIAL_RIGHT_PHOTO

async def facial_right_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.photo:
        await update.message.reply_text(get_text("facial_send_photo", get_user_language(update.effective_user.id, None)))
        return FACIAL_RIGHT_PHOTO
    
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp_path = tmp.name
    await file.download_to_drive(tmp_path)
    
    is_valid, reason = check_image_quality(tmp_path)
    if not is_valid:
        os.unlink(tmp_path)
        lang = get_user_language(update.effective_user.id, None) or 'fa'
        await update.message.reply_text(
            get_text("facial_quality_reject", lang).format(reason=reason)
        )
        return FACIAL_RIGHT_PHOTO
    
    context.user_data['facial_right_photo'] = tmp_path
    lang = get_user_language(update.effective_user.id, None) or 'fa'
    await update.message.reply_text(get_text("facial_accept_photo", lang))
    await update.message.reply_text(get_text("facial_ask_left_photo", lang))
    return FACIAL_LEFT_PHOTO

async def facial_left_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.photo:
        await update.message.reply_text(get_text("facial_send_photo", get_user_language(update.effective_user.id, None)))
        return FACIAL_LEFT_PHOTO
    
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp_path = tmp.name
    await file.download_to_drive(tmp_path)
    
    is_valid, reason = check_image_quality(tmp_path)
    if not is_valid:
        os.unlink(tmp_path)
        lang = get_user_language(update.effective_user.id, None) or 'fa'
        await update.message.reply_text(
            get_text("facial_quality_reject", lang).format(reason=reason)
        )
        return FACIAL_LEFT_PHOTO
    
    context.user_data['facial_left_photo'] = tmp_path
    lang = get_user_language(update.effective_user.id, None) or 'fa'
    await update.message.reply_text(get_text("facial_analyzing", lang))
    
    # Start analysis
    await perform_facial_analysis(update, context)
    return ConversationHandler.END

async def perform_facial_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Core analysis logic."""
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        # Get patient
        patient = db.query(Patient).filter_by(telegram_id=user_id).first()
        if not patient:
            await update.message.reply_text("Patient not found.")
            return
        
        # Process images
        front_path = context.user_data.get('facial_front_photo')
        right_path = context.user_data.get('facial_right_photo')
        left_path = context.user_data.get('facial_left_photo')
        gender = context.user_data.get('facial_gender', 'unknown')
        age = context.user_data.get('facial_age', 30)
        
        # Extract landmarks using MediaPipe
        from utils.facial_metrics import compute_facial_metrics
        import mediapipe as mp
        import cv2
        
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)
        
        landmarks_data = {}
        for view, path in [('front', front_path), ('right', right_path), ('left', left_path)]:
            if path and os.path.exists(path):
                img = cv2.imread(path)
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb)
                if results.multi_face_landmarks:
                    lm = results.multi_face_landmarks[0].landmark
                    points = [(int(l.x * img.shape[1]), int(l.y * img.shape[0])) for l in lm]
                    landmarks_data[view] = points
        
        if not landmarks_data:
            await update.message.reply_text("Could not extract facial landmarks. Please try with better photos.")
            return
        
        # Compute metrics from front view
        metrics = compute_facial_metrics(landmarks_data.get('front', []))
        
        # Generate analysis text using LLM
        analysis_prompt = f"""
        You are a medical aesthetics AI. Analyze the following facial metrics and provide a professional aesthetic recommendation.
        Metrics: {metrics}
        Gender: {gender}, Age: {age}
        
        Provide:
        1. A brief summary of facial features
        2. Recommendations for treatments (Botox, Filler, Mesotherapy, etc.)
        3. Priority order of treatments
        4. Estimated units/volume if applicable
        5. A disclaimer that this is not a medical diagnosis.
        
        Keep the response professional and empathetic.
        """
        
        llm_response = await _router.generate(analysis_prompt, task="facial_analysis")
        
        # Parse LLM response (simplified - in production, use structured parsing)
        # For now, we store the raw response and extract basic scores from metrics
        
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
            report_text=llm_response,
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
        
        # Generate recommendations from LLM response (simplified)
        # For production, you'd parse structured output
        recs = [
            TreatmentRecommendation(
                analysis_id=analysis.id,
                treatment_type='Botox',
                area='Forehead',
                estimated_units='20-30',
                confidence=0.8,
                priority=1,
                description='Reduce forehead wrinkles',
            ),
            TreatmentRecommendation(
                analysis_id=analysis.id,
                treatment_type='Filler',
                area='Cheeks',
                estimated_volume='1-2 cc',
                confidence=0.75,
                priority=2,
                description='Restore midface volume',
            )
        ]
        for rec in recs:
            db.add(rec)
        
        # Record usage for patient
        role = get_user_role(user_id, db)
        if role == 'patient':
            usage = db.query(FacialAnalysisUsage).filter_by(patient_id=patient.id).first()
            if not usage:
                usage = FacialAnalysisUsage(patient_id=patient.id)
                db.add(usage)
            usage.analysis_used = True
            usage.used_at = datetime.utcnow()
        
        db.commit()
        
        # Generate PDF report
        pdf_path = generate_facial_report({
            'patient_name': patient.name,
            'gender': gender,
            'age': age,
            'overall_beauty': metrics.get('overall_beauty', 0),
            'symmetry': metrics.get('eye_symmetry', 0),
            'skin_quality': metrics.get('skin_quality', 0),
            'youthfulness': metrics.get('youthfulness', 0),
            'volume_balance': metrics.get('volume_balance', 0),
            'harmony': metrics.get('facial_harmony', 0),
            'recommendations': [{'treatment_type': 'Botox', 'area': 'Forehead', 'priority': 1, 'estimated_units': '20-30'}]
        }, language='fa')
        
        # Send report
        lang = get_user_language(user_id, db) or 'fa'
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
        
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                await update.message.reply_document(f, filename='facial_analysis_report.pdf')
            os.unlink(pdf_path)
        else:
            await update.message.reply_text(llm_response[:3000])  # Truncate if needed
        
        # Cleanup images
        for path in [front_path, right_path, left_path]:
            if path and os.path.exists(path):
                os.unlink(path)
        
    except Exception as e:
        logger.error(f"Facial analysis error: {e}")
        await update.message.reply_text("An error occurred during analysis. Please try again later.")
    finally:
        db.close()
