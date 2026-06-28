# models/facial_models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from models import Base
from datetime import datetime

class FacialAnalysis(Base):
    __tablename__ = 'facial_analyses'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    clinic_id = Column(Integer, ForeignKey('clinics.id'))
    performed_by = Column(Integer, ForeignKey('staff.id'))
    gender = Column(String(10))
    age = Column(Integer)
    overall_beauty_score = Column(Float)
    symmetry_score = Column(Float)
    skin_quality_score = Column(Float)
    youthfulness_score = Column(Float)
    volume_balance_score = Column(Float)
    facial_harmony_score = Column(Float)
    estimated_apparent_age = Column(Integer)
    report_text = Column(Text)
    report_pdf_url = Column(String(500), nullable=True)
    status = Column(String(20), default='completed')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FacialLandmarks(Base):
    __tablename__ = 'facial_landmarks'
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('facial_analyses.id'))
    view = Column(String(10))
    landmarks = Column(JSON)
    confidence = Column(Float)

class FacialMetrics(Base):
    __tablename__ = 'facial_metrics'
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('facial_analyses.id'))
    metric_name = Column(String(50))
    value = Column(Float)
    confidence = Column(Float)
    category = Column(String(30))

class TreatmentRecommendation(Base):
    __tablename__ = 'treatment_recommendations'
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('facial_analyses.id'))
    treatment_type = Column(String(30))
    area = Column(String(50))
    estimated_units = Column(String(20), nullable=True)
    estimated_volume = Column(String(20), nullable=True)
    confidence = Column(Float)
    priority = Column(Integer)
    description = Column(Text)
    price_estimate = Column(Float, nullable=True)

class BeforeAfter(Base):
    __tablename__ = 'before_after'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    before_analysis_id = Column(Integer, ForeignKey('facial_analyses.id'))
    after_analysis_id = Column(Integer, ForeignKey('facial_analyses.id'))
    treatment_done = Column(JSON)
    improvement_symmetry = Column(Float)
    improvement_skin = Column(Float)
    improvement_volume = Column(Float)
    improvement_overall = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class FacialAnalysisUsage(Base):
    __tablename__ = 'facial_analysis_usage'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), unique=True)
    analysis_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
