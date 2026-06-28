# services/pdf_generator.py
import os
import tempfile
import logging
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

logger = logging.getLogger(__name__)

def generate_facial_report(analysis_data: dict, language: str = 'fa') -> str:
    """
    Generate a PDF report for facial analysis.
    Returns file path of the generated PDF.
    """
    try:
        # Create temporary file
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_path = tmp_file.name
        tmp_file.close()
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Add custom style for Persian/Arabic support if needed
        try:
            # Try to load a font that supports Persian/Arabic
            font_path = os.getenv('PDF_REPORT_FONT_PATH', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                styles.add(ParagraphStyle(name='CustomBody', fontName='CustomFont', fontSize=10, leading=14))
                styles.add(ParagraphStyle(name='CustomTitle', fontName='CustomFont', fontSize=16, leading=20, alignment=1))
            else:
                styles.add(ParagraphStyle(name='CustomBody', fontName='Helvetica', fontSize=10, leading=14))
                styles.add(ParagraphStyle(name='CustomTitle', fontName='Helvetica', fontSize=16, leading=20, alignment=1))
        except:
            styles.add(ParagraphStyle(name='CustomBody', fontName='Helvetica', fontSize=10, leading=14))
            styles.add(ParagraphStyle(name='CustomTitle', fontName='Helvetica', fontSize=16, leading=20, alignment=1))
        
        # Build content
        content = []
        
        # Title
        title_text = analysis_data.get('title', 'Facial Analysis Report')
        content.append(Paragraph(title_text, styles['CustomTitle']))
        content.append(Spacer(1, 0.2*inch))
        
        # Patient info
        info_text = f"Patient: {analysis_data.get('patient_name', 'N/A')}<br/>"
        info_text += f"Gender: {analysis_data.get('gender', 'N/A')}<br/>"
        info_text += f"Age: {analysis_data.get('age', 'N/A')}<br/>"
        info_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        content.append(Paragraph(info_text, styles['CustomBody']))
        content.append(Spacer(1, 0.2*inch))
        
        # Scores
        scores = [
            ['Metric', 'Score'],
            ['Overall Beauty', f"{analysis_data.get('overall_beauty', 0):.1f}"],
            ['Symmetry', f"{analysis_data.get('symmetry', 0):.1f}"],
            ['Skin Quality', f"{analysis_data.get('skin_quality', 0):.1f}"],
            ['Youthfulness', f"{analysis_data.get('youthfulness', 0):.1f}"],
            ['Volume Balance', f"{analysis_data.get('volume_balance', 0):.1f}"],
            ['Facial Harmony', f"{analysis_data.get('harmony', 0):.1f}"],
        ]
        table = Table(scores, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        content.append(table)
        content.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        if analysis_data.get('recommendations'):
            content.append(Paragraph('Recommendations', styles['CustomTitle']))
            for rec in analysis_data['recommendations']:
                rec_text = f"• {rec.get('treatment_type', '')} - {rec.get('area', '')} "
                rec_text += f"(Priority: {rec.get('priority', 0)})"
                if rec.get('estimated_units'):
                    rec_text += f" - Units: {rec['estimated_units']}"
                if rec.get('estimated_volume'):
                    rec_text += f" - Volume: {rec['estimated_volume']}"
                content.append(Paragraph(rec_text, styles['CustomBody']))
            content.append(Spacer(1, 0.1*inch))
        
        # Disclaimer
        disclaimer = "⚠️ This analysis is for informational purposes only. "
        disclaimer += "All treatment decisions must be made by a licensed medical professional "
        disclaimer += "after a complete clinical evaluation."
        content.append(Paragraph(disclaimer, styles['CustomBody']))
        
        # Build PDF
        doc.build(content)
        return pdf_path
    
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return None
