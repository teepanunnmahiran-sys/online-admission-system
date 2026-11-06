"""
Online Student Admission System - FastAPI Backend Server
Integrates Student Registration, Thai ID Checksum Validation, Document Review,
Auto Student ID Generation, Analytics Dashboard, and Standard ศธ.02 Export.
"""
import os
import sqlite3
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import database
from export_service import generate_std02_excel, generate_std02_csv, MAJOR_CODES, resolve_major_code
from barcode_util import generate_qr_code_base64, generate_code128_svg

app = FastAPI(title="ระบบรับสมัครเรียนออนไลน์ครบวงจร (Online Admission System)")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Mount Static Files & Templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Ensure Database is initialized
database.init_db()

# --------------------------------------------------------------------------
# Pydantic Schemas
# --------------------------------------------------------------------------
class RegisterPayload(BaseModel):
    citizen_id: str
    prefix_th: str
    first_name_th: str
    last_name_th: str
    first_name_en: Optional[str] = None
    last_name_en: Optional[str] = None
    gender: str
    birth_date: str
    nationality: Optional[str] = "ไทย"
    religion: Optional[str] = "พุทธ"
    phone: str
    email: Optional[str] = None
    address_no: str
    moo: Optional[str] = ""
    subdistrict: str
    district: str
    province: str
    postal_code: str
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    guardian_name: str
    guardian_phone: str
    guardian_relation: str
    education_level: str
    first_choice_major: str
    second_choice_major: Optional[str] = None
    quota_type: Optional[str] = "สอบคัดเลือกทั่วไป"
    old_school: str
    old_school_province: str
    gpa: float = 3.00
    referrer: Optional[str] = "Facebook/TikTok"

class StatusUpdatePayload(BaseModel):
    status: str
    admin_notes: Optional[str] = ""

# --------------------------------------------------------------------------
# Routes: Web Pages
# --------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main Web Application (Single-Page App)"""
    return templates.TemplateResponse(request=request, name="index.html")

# --------------------------------------------------------------------------
# Routes: Applicant APIs
# --------------------------------------------------------------------------
@app.post("/api/applicants/register")
async def register_applicant(payload: RegisterPayload):
    """
    Register new applicant with Thai ID checksum validation
    """
    clean_cid = payload.citizen_id.replace("-", "").strip()
    
    # 1. Validate Thai ID Checksum
    if len(clean_cid) != 13 or not clean_cid.isdigit():
        raise HTTPException(status_code=400, detail="เลขประจำตัวประชาชนต้องเป็นตัวเลข 13 หลัก")
    
    s = sum(int(clean_cid[i]) * (13 - i) for i in range(12))
    check_digit = (11 - (s % 11)) % 10
    if check_digit != int(clean_cid[12]):
        raise HTTPException(status_code=400, detail="เลขประจำตัวประชาชนไม่ถูกต้องตามสูตรคำนวณ (Invalid Check Digit)")

    conn = database.get_db()
    cursor = conn.cursor()

    # 2. Check duplicate submission
    cursor.execute("SELECT id FROM applicants WHERE citizen_id = ?", (clean_cid,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="เลขประจำตัวประชาชนนี้ได้ทำการสมัครในระบบแล้ว กรุณาตรวจสอบสถานะในแท็บที่ 2")

    # 3. Insert Applicant Record
    cursor.execute("""
    INSERT INTO applicants (
        citizen_id, prefix_th, first_name_th, last_name_th, first_name_en, last_name_en,
        gender, birth_date, nationality, religion, phone, email, address_no, moo, subdistrict,
        district, province, postal_code, father_name, mother_name, guardian_name,
        guardian_phone, guardian_relation, education_level, first_choice_major,
        second_choice_major, quota_type, old_school, old_school_province, gpa,
        referrer, status, admin_notes
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'รอตรวจสอบ', 'ได้รับใบสมัครเข้าสู่ระบบแล้ว รอเจ้าหน้าที่ตรวจสอบเอกสาร'
    )
    """, (
        clean_cid, payload.prefix_th, payload.first_name_th, payload.last_name_th,
        payload.first_name_en, payload.last_name_en, payload.gender, payload.birth_date,
        payload.nationality, payload.religion, payload.phone, payload.email,
        payload.address_no, payload.moo, payload.subdistrict, payload.district,
        payload.province, payload.postal_code, payload.father_name, payload.mother_name,
        payload.guardian_name, payload.guardian_phone, payload.guardian_relation,
        payload.education_level, payload.first_choice_major, payload.second_choice_major,
        payload.quota_type, payload.old_school, payload.old_school_province,
        payload.gpa, payload.referrer
    ))
    applicant_id = cursor.lastrowid

    # 4. Attach standard document slots
    doc_types = [
        ("photo", f"photo_{clean_cid}.jpg"),
        ("id_card", f"id_card_{clean_cid}.pdf"),
        ("house_reg", f"house_reg_{clean_cid}.pdf"),
        ("transcript", f"transcript_{clean_cid}.pdf")
    ]
    for dtype, fname in doc_types:
        cursor.execute("""
        INSERT INTO documents (applicant_id, doc_type, filename, file_path, status, comment)
        VALUES (?, ?, ?, ?, 'รอตรวจ', 'รอเจ้าหน้าที่เปิดตรวจ')
        """, (applicant_id, dtype, fname, f"/static/uploads/{fname}"))

    # 5. Log & Notification Simulation
    log_msg = f"ผู้สมัครใหม่: {payload.prefix_th}{payload.first_name_th} {payload.last_name_th} ระดับ {payload.education_level} สาขา {payload.first_choice_major}"
    cursor.execute("INSERT INTO system_logs (action, target, details) VALUES (?, ?, ?)",
                   ("NEW_APPLICATION", clean_cid, log_msg))
    
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": "บันทึกใบสมัครสำเร็จ",
        "applicant_id": applicant_id,
        "citizen_id": clean_cid
    }

@app.get("/api/applicants/status/{citizen_id}")
async def get_applicant_status(citizen_id: str):
    """
    Search applicant progress, checklist, and notes by 13-digit citizen ID
    """
    clean_cid = citizen_id.replace("-", "").strip()
    conn = database.get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applicants WHERE citizen_id = ?", (clean_cid,))
    app_row = cursor.fetchone()

    if not app_row:
        conn.close()
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้สมัคร")

    app_dict = dict(app_row)

    # Fetch documents
    cursor.execute("SELECT * FROM documents WHERE applicant_id = ?", (app_dict["id"],))
    docs = [dict(r) for r in cursor.fetchall()]
    app_dict["documents"] = docs

    conn.close()
    return app_dict

@app.post("/api/applicants/update-docs")
async def update_applicant_documents(
    applicant_id: int = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Re-upload document when status was 'เอกสารไม่สมบูรณ์'
    """
    conn = database.get_db()
    cursor = conn.cursor()

    # Update document record
    cursor.execute("""
    UPDATE documents
    SET filename = ?, status = 'รอตรวจ', comment = 'อัปโหลดเอกสารแก้ไขใหม่แล้ว'
    WHERE applicant_id = ? AND doc_type = ?
    """, (file.filename, applicant_id, doc_type))

    # Update applicant status back to 'รอตรวจสอบ'
    cursor.execute("""
    UPDATE applicants
    SET status = 'รอตรวจสอบ', admin_notes = 'ผู้สมัครได้ส่งเอกสารแก้ไขเรียบร้อยแล้ว รอการตรวจซ้ำ'
    WHERE id = ?
    """, (applicant_id,))

    conn.commit()
    conn.close()
    return {"status": "success", "message": "อัปโหลดเอกสารสำเร็จ"}

# --------------------------------------------------------------------------
# Routes: Print-Ready PDF Templates
# --------------------------------------------------------------------------
@app.get("/api/applicants/{citizen_id}/application-pdf", response_class=HTMLResponse)
async def generate_application_pdf(request: Request, citizen_id: str):
    """
    Renders official Student Application Form (ใบสมัครเข้าศึกษาต่อ)
    Complete with vector Code 128 barcode and QR Code.
    """
    clean_cid = citizen_id.replace("-", "").strip()
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants WHERE citizen_id = ?", (clean_cid,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้สมัคร")

    app_data = dict(row)

    # Format Thai today date
    today = datetime.now()
    thai_year = today.year + 543
    thai_months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    today_thai = f"{today.day} {thai_months[today.month]} พ.ศ. {thai_year}"

    # Generate QR Code & SVG Barcode
    qr_data = f"VERIFY:APP:{app_data['id']}:CID:{clean_cid}"
    qr_b64 = generate_qr_code_base64(qr_data)
    barcode_svg = generate_code128_svg(clean_cid, height=45, bar_width=2)

    return templates.TemplateResponse(request=request, name="application_pdf.html", context={
        "app": app_data,
        "qr_code": qr_b64,
        "barcode_svg": barcode_svg,
        "today_date": today_thai
    })

@app.get("/api/applicants/{citizen_id}/enrollment-pdf", response_class=HTMLResponse)
async def generate_enrollment_pdf(request: Request, citizen_id: str):
    """
    Renders official Student Enrollment & Guarantee Contract (ใบมอบตัวและสัญญาค้ำประกัน)
    """
    clean_cid = citizen_id.replace("-", "").strip()
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants WHERE citizen_id = ?", (clean_cid,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้สมัคร")

    app_data = dict(row)

    today = datetime.now()
    thai_year = today.year + 543
    thai_months = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    today_thai = f"{today.day} {thai_months[today.month]} พ.ศ. {thai_year}"

    student_code = app_data.get("student_id") or clean_cid
    qr_data = f"ENROLL:{student_code}:CID:{clean_cid}"
    qr_b64 = generate_qr_code_base64(qr_data)
    barcode_svg = generate_code128_svg(student_code, height=45, bar_width=2)

    return templates.TemplateResponse(request=request, name="enrollment_pdf.html", context={
        "app": app_data,
        "qr_code": qr_b64,
        "barcode_svg": barcode_svg,
        "today_date": today_thai
    })

# --------------------------------------------------------------------------
# Routes: Admin & Registrar APIs
# --------------------------------------------------------------------------
@app.get("/api/admin/analytics")
async def get_admin_analytics():
    """
    Real-time analytics summary for dashboard charts and metrics cards
    """
    conn = database.get_db()
    cursor = conn.cursor()

    # Overall Counts
    cursor.execute("SELECT COUNT(*) FROM applicants")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applicants WHERE status = 'รอตรวจสอบ'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applicants WHERE status = 'ผ่านการคัดเลือก'")
    passed = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applicants WHERE status = 'มอบตัวแล้ว'")
    enrolled = cursor.fetchone()[0]

    # By Major
    cursor.execute("SELECT first_choice_major, COUNT(*) FROM applicants GROUP BY first_choice_major")
    by_major = {row[0]: row[1] for row in cursor.fetchall()}

    # By Level
    cursor.execute("SELECT education_level, COUNT(*) FROM applicants GROUP BY education_level")
    by_level = {row[0]: row[1] for row in cursor.fetchall()}

    # By Referrer
    cursor.execute("SELECT referrer, COUNT(*) FROM applicants GROUP BY referrer")
    by_referrer = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    return {
        "total_applicants": total,
        "pending_review": pending,
        "passed": passed,
        "enrolled": enrolled,
        "by_major": by_major,
        "by_level": by_level,
        "by_referrer": by_referrer
    }

@app.get("/api/admin/applicants")
async def get_all_applicants():
    """List all applicants for admin table"""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.get("/api/admin/applicants/{applicant_id}")
async def get_applicant_detail(applicant_id: int):
    """Get single applicant with documents for review modal"""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")

    app_data = dict(row)
    cursor.execute("SELECT * FROM documents WHERE applicant_id = ?", (applicant_id,))
    app_data["documents"] = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return app_data

@app.put("/api/admin/applicants/{applicant_id}/status")
async def update_applicant_status(applicant_id: int, payload: StatusUpdatePayload):
    """Change applicant status (ผ่านการคัดเลือก, เอกสารไม่สมบูรณ์, etc.)"""
    conn = database.get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE applicants
    SET status = ?, admin_notes = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (payload.status, payload.admin_notes, applicant_id))

    cursor.execute("INSERT INTO system_logs (action, target, details) VALUES (?, ?, ?)",
                   ("STATUS_UPDATE", str(applicant_id), f"เปลี่ยนสถานะเป็น {payload.status}: {payload.admin_notes}"))

    conn.commit()
    conn.close()
    return {"status": "success", "message": "อัปเดตสถานะสำเร็จ"}

@app.post("/api/admin/applicants/{applicant_id}/enroll")
async def enroll_applicant(applicant_id: int):
    """
    Enroll student and automatically issue standardized Student ID
    Formula: [ปี พ.ศ. 2 หลัก เช่น 68][ระดับชั้น 2=ปวช, 3=ปวส][รหัสสาขาวิชา 4 หลัก][ลำดับ 4 หลัก]
    """
    conn = database.get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลผู้สมัคร")

    app_data = dict(row)
    level_code = "2" if app_data["education_level"] == "ปวช." else "3"
    major_code = resolve_major_code(app_data["education_level"], app_data["first_choice_major"])
    major_suffix = major_code[-4:]  # Last 4 digits

    year_prefix = "68"
    prefix_id = f"{year_prefix}{level_code}{major_suffix}"

    # Count how many already enrolled in this major to get sequence number
    cursor.execute("SELECT COUNT(*) FROM enrollments WHERE student_id LIKE ?", (f"{prefix_id}%",))
    count = cursor.fetchone()[0]
    seq_num = f"{count + 1:04d}"
    new_student_id = f"{prefix_id}{seq_num}"

    # Insert enrollment record
    cursor.execute("""
    INSERT OR REPLACE INTO enrollments (applicant_id, student_id, guardian_name, guardian_phone, guardian_relation, witness_name, enrolled_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        applicant_id,
        new_student_id,
        app_data.get("guardian_name") or "ผู้ปกครอง",
        app_data.get("guardian_phone") or app_data["phone"],
        app_data.get("guardian_relation") or "ผู้ปกครอง",
        "อาจารย์สมศักดิ์ มั่นใจ (หัวหน้างานทะเบียน)",
        datetime.now().strftime("%Y-%m-%d")
    ))

    # Update applicant record
    cursor.execute("""
    UPDATE applicants
    SET status = 'มอบตัวแล้ว', student_id = ?, admin_notes = 'มอบตัวเสร็จสิ้น ออกรหัสนักศึกษาเรียบร้อย'
    WHERE id = ?
    """, (new_student_id, applicant_id))

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "student_id": new_student_id,
        "message": f"มอบตัวสำเร็จ รหัสนักศึกษาใหม่: {new_student_id}"
    }

# --------------------------------------------------------------------------
# Routes: Export Data for Standard ศธ.02
# --------------------------------------------------------------------------
@app.get("/api/admin/export/std02")
async def export_std02_file(format: str = "xlsx"):
    """
    Direct export into Standardized ศธ.02 Format (.xlsx or .csv)
    Ready to import into Vocational Registry Central Database.
    """
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applicants ORDER BY education_level, first_choice_major, id")
    applicants = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if format.lower() == "csv":
        csv_bytes = generate_std02_csv(applicants)
        return Response(
            content=csv_bytes,
            media_type="text/csv; charset=utf-8-sig",
            headers={
                "Content-Disposition": f"attachment; filename=std02_import_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            }
        )
    else:
        excel_bytes = generate_std02_excel(applicants)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=std02_vocational_students_2568.xlsx"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
