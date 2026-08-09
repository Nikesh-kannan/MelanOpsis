import uuid
import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.config import IMAGES_DIR
from app.db.database import get_db
from app.db.models import Case
from app.db.schemas import AnalyzeResponse
from app.models.inference import inference_service

router = APIRouter()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

import cv2
import io
from fastapi.responses import Response

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format '{file.content_type}'. Please upload JPEG, PNG, or WEBP images."
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image size exceeds maximum limit of 15MB.")
    
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 1. Run inference & preprocessing
    try:
        prediction = inference_service.predict(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image preprocessing or model inference failed: {str(e)}")

    # 2. Save original image to disk
    case_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ".jpg"
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"
    
    filename = f"{case_id}{ext}"
    filepath = IMAGES_DIR / filename
    
    async with aiofiles.open(filepath, "wb") as out_file:
        await out_file.write(contents)
        
    image_url = f"/data/images/{filename}"

    # 3. Save Grad-CAM heatmap overlay to disk if generated
    gradcam_url = None
    if "gradcam_bgr" in prediction and prediction["gradcam_bgr"] is not None:
        gradcam_filename = f"gradcam_{case_id}.jpg"
        gradcam_filepath = IMAGES_DIR / gradcam_filename
        cv2.imwrite(str(gradcam_filepath), prediction["gradcam_bgr"])
        gradcam_url = f"/data/images/{gradcam_filename}"

    # 4. Log record to SQLite DB
    db_case = Case(
        case_id=case_id,
        image_filename=filename,
        image_url=image_url,
        result=prediction["result"],
        confidence=prediction["confidence"],
        risk_score=prediction["risk_score"],
        processing_time_ms=prediction["processing_time_ms"],
        patient_id="Unassigned Patient",
        notes=""
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)

    return AnalyzeResponse(
        result=prediction["result"],
        confidence=prediction["confidence"],
        risk_score=prediction["risk_score"],
        processing_time_ms=prediction["processing_time_ms"],
        case_id=case_id,
        image_url=image_url,
        gradcam_heatmap_url=gradcam_url,
        sub_diagnoses=prediction.get("sub_diagnoses", [])
    )


@router.post("/analyze/pdf")
async def generate_pdf_report(
    case_id: str,
    patient_id: str = "PAT-8842",
    notes: str = "Routine point-of-care dermatoscopic triage.",
    db: Session = Depends(get_db)
):
    """
    Generates a downloadable clinical referral PDF report for a case.
    """
    db_case = db.query(Case).filter(Case.case_id == case_id).first()
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")

    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    # Title & Header
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )
    story.append(Paragraph("MelanOpsis AI — Clinical Lesion Triage Report", title_style))
    story.append(Paragraph("Open Source AI Decision Support Platform | Tele-Dermatology Referral Slip", subtitle_style))
    story.append(Spacer(1, 15))

    # Patient & Summary Table
    is_refer = db_case.result == 'refer'
    status_text = "REFER FOR REVIEW (High-Risk Detected)" if is_refer else "NO FLAG RAISED (Benign Mole)"
    status_color = colors.HexColor('#DC2626') if is_refer else colors.HexColor('#16A34A')

    summary_data = [
        [Paragraph("<b>Case ID:</b>", styles['Normal']), Paragraph(db_case.case_id, styles['Normal']),
         Paragraph("<b>Date/Time:</b>", styles['Normal']), Paragraph(db_case.created_at.strftime("%Y-%m-%d %H:%M UTC"), styles['Normal'])],
        [Paragraph("<b>Patient ID:</b>", styles['Normal']), Paragraph(patient_id, styles['Normal']),
         Paragraph("<b>Risk Score:</b>", styles['Normal']), Paragraph(f"{db_case.risk_score*100:.1f}%", styles['Normal'])],
        [Paragraph("<b>Triage Decision:</b>", styles['Normal']), Paragraph(f"<font color='{status_color.hexval()}'><b>{status_text}</b></font>", styles['Normal']),
         Paragraph("<b>Confidence:</b>", styles['Normal']), Paragraph(f"{db_case.confidence*100:.1f}%", styles['Normal'])],
    ]
    t = Table(summary_data, colWidths=[100, 170, 100, 170])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Image Insertion if available
    img_path = IMAGES_DIR / db_case.image_filename
    if os.path.exists(img_path):
        try:
            rl_img = RLImage(str(img_path), width=220, height=185)
            gradcam_file = IMAGES_DIR / f"gradcam_{db_case.case_id}.jpg"
            if os.path.exists(gradcam_file):
                rl_grad = RLImage(str(gradcam_file), width=220, height=185)
                img_table = Table([[rl_img, rl_grad], [Paragraph("<b>Original Lesion Photo</b>", styles['Normal']), Paragraph("<b>Grad-CAM Attention Heatmap 🔥</b>", styles['Normal'])]], colWidths=[270, 270])
            else:
                img_table = Table([[rl_img], [Paragraph("<b>Original Lesion Photo</b>", styles['Normal'])]], colWidths=[540])
            img_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
            story.append(img_table)
        except Exception as e:
            print(f"PDF Image insert error: {e}")

    story.append(Spacer(1, 15))

    # Clinical Next Steps & Disclaimer
    rec_title = ParagraphStyle('RecTitle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#0F172A'))
    story.append(Paragraph("Recommended Clinical Protocol", rec_title))
    rec_text = "Schedule specialist referral or tele-dermatology review within 7-14 days. Perform ABCDE dermatoscope inspection." if is_refer else "No immediate high-risk features detected. Advise patient to monitor for ABCDE changes (Asymmetry, Border, Color, Diameter, Evolution)."
    story.append(Paragraph(rec_text, styles['Normal']))
    story.append(Spacer(1, 15))

    disc_style = ParagraphStyle('DiscStyle', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=11, textColor=colors.HexColor('#64748B'))
    story.append(Paragraph("<b>Medical Disclaimer:</b> MelanOpsis AI is a clinical decision support tool designed for triage assistance, not definitive diagnosis. Final clinical management must follow registered medical officer evaluation.", disc_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=MelanOpsis_Report_{case_id[:8]}.pdf"})
