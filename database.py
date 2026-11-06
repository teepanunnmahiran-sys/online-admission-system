"""
Database schema, initialization, and data layer for Online Admission System
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "admission.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_thai_id_check_digit(first_12_digits: str) -> str:
    """Calculate the 13th check digit for a 12-digit Thai ID prefix"""
    s = sum(int(digit) * (13 - idx) for idx, digit in enumerate(first_12_digits))
    check_digit = (11 - (s % 11)) % 10
    return str(check_digit)

def make_valid_thai_id(prefix12: str) -> str:
    return prefix12 + calculate_thai_id_check_digit(prefix12)

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Table: applicants
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applicants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        citizen_id TEXT UNIQUE NOT NULL,
        prefix_th TEXT NOT NULL,
        first_name_th TEXT NOT NULL,
        last_name_th TEXT NOT NULL,
        first_name_en TEXT,
        last_name_en TEXT,
        gender TEXT NOT NULL,
        birth_date TEXT NOT NULL,
        nationality TEXT DEFAULT 'ไทย',
        religion TEXT DEFAULT 'พุทธ',
        phone TEXT NOT NULL,
        email TEXT,
        address_no TEXT,
        moo TEXT,
        subdistrict TEXT,
        district TEXT,
        province TEXT,
        postal_code TEXT,
        father_name TEXT,
        father_phone TEXT,
        mother_name TEXT,
        mother_phone TEXT,
        guardian_name TEXT,
        guardian_phone TEXT,
        guardian_relation TEXT,
        education_level TEXT NOT NULL, -- ปวช. หรือ ปวส.
        first_choice_major TEXT NOT NULL,
        second_choice_major TEXT,
        quota_type TEXT DEFAULT 'สอบคัดเลือกทั่วไป',
        old_school TEXT,
        old_school_province TEXT,
        gpa REAL DEFAULT 3.00,
        referrer TEXT DEFAULT 'Facebook/TikTok',
        status TEXT DEFAULT 'รอตรวจสอบ', -- รอตรวจสอบ, เอกสารไม่สมบูรณ์, ผ่านการคัดเลือก, มอบตัวแล้ว, สละสิทธิ์
        admin_notes TEXT,
        student_id TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table: documents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        applicant_id INTEGER NOT NULL,
        doc_type TEXT NOT NULL, -- photo, id_card, house_reg, transcript
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        status TEXT DEFAULT 'รอตรวจ', -- รอตรวจ, ถูกต้อง, ต้องแก้ไข
        comment TEXT,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (applicant_id) REFERENCES applicants (id) ON DELETE CASCADE
    );
    """)

    # Table: enrollments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        applicant_id INTEGER UNIQUE NOT NULL,
        student_id TEXT UNIQUE NOT NULL,
        guardian_name TEXT NOT NULL,
        guardian_phone TEXT NOT NULL,
        guardian_relation TEXT NOT NULL,
        witness_name TEXT NOT NULL,
        enrolled_date TEXT NOT NULL,
        academic_year TEXT DEFAULT '2568',
        semester TEXT DEFAULT '1',
        fee_paid INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (applicant_id) REFERENCES applicants (id) ON DELETE CASCADE
    );
    """)

    # Table: system_logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        target TEXT,
        details TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    # Seed initial realistic test data if empty
    cursor.execute("SELECT COUNT(*) FROM applicants")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()

    # Generate 6 realistic sample applicants
    samples = [
        {
            "id_prefix": "110070123456",
            "prefix": "นาย",
            "first_th": "สมชาย",
            "last_th": "ใจดีมั่นคง",
            "first_en": "Somchai",
            "last_en": "Jaideemankong",
            "gender": "ชาย",
            "birth": "2008-05-14",
            "phone": "081-234-5678",
            "email": "somchai.j@gmail.com",
            "address": "123/45", "moo": "3", "subdistrict": "บางเขน", "district": "เมือง", "province": "นนทบุรี", "zip": "11000",
            "father": "นายวิชัย ใจดีมั่นคง", "father_phone": "089-111-2233",
            "mother": "นางสมศรี ใจดีมั่นคง", "mother_phone": "089-444-5566",
            "guardian": "นายวิชัย ใจดีมั่นคง", "guardian_phone": "089-111-2233", "guardian_rel": "บิดา",
            "level": "ปวช.",
            "major1": "ช่างยนต์",
            "major2": "ช่างไฟฟ้ากำลัง",
            "quota": "โควตารับตรง/เรียนดี",
            "old_school": "โรงเรียนนนทบุรีพิทยาคม",
            "old_province": "นนทบุรี",
            "gpa": 3.75,
            "referrer": "ครูแนะแนว",
            "status": "ผ่านการคัดเลือก",
            "notes": "เอกสารครบถ้วน ผลการเรียนดีเด่น มีสิทธิ์มอบตัว",
            "student_id": None
        },
        {
            "id_prefix": "120090045678",
            "prefix": "นางสาว",
            "first_th": "กนกพร",
            "last_th": "รักการเรียน",
            "first_en": "Kanokporn",
            "last_en": "Rakkarnrien",
            "gender": "หญิง",
            "birth": "2006-11-20",
            "phone": "089-876-5432",
            "email": "kanokporn.r@gmail.com",
            "address": "88/12", "moo": "1", "subdistrict": "คลองหนึ่ง", "district": "คลองหลวง", "province": "ปทุมธานี", "zip": "12120",
            "father": "นายประเสริฐ รักการเรียน", "father_phone": "081-222-3344",
            "mother": "นางสุจิตรา รักการเรียน", "mother_phone": "081-555-6677",
            "guardian": "นางสุจิตรา รักการเรียน", "guardian_phone": "081-555-6677", "guardian_rel": "มารดา",
            "level": "ปวส.",
            "major1": "เทคโนโลยีธุรกิจดิจิทัล",
            "major2": "การบัญชี",
            "quota": "สอบคัดเลือกทั่วไป",
            "old_school": "วิทยาลัยอาชีวศึกษาปทุมธานี",
            "old_province": "ปทุมธานี",
            "gpa": 3.42,
            "referrer": "Facebook/TikTok",
            "status": "มอบตัวแล้ว",
            "notes": "มอบตัวและชำระค่าธรรมเนียมเรียบร้อยแล้ว",
            "student_id": "68302040001"
        },
        {
            "id_prefix": "130080011223",
            "prefix": "นาย",
            "first_th": "ธนากร",
            "last_th": "เจริญศิลป์",
            "first_en": "Thanakorn",
            "last_en": "Charoensilp",
            "gender": "ชาย",
            "birth": "2008-08-08",
            "phone": "095-123-9988",
            "email": "thanakorn.c@hotmail.com",
            "address": "55 หมู่บ้านสุขสันต์", "moo": "5", "subdistrict": "บางรักน้อย", "district": "เมือง", "province": "นนทบุรี", "zip": "11000",
            "father": "นายธวัช เจริญศิลป์", "father_phone": "082-333-4455",
            "mother": "นางศิริพร เจริญศิลป์", "mother_phone": "082-666-7788",
            "guardian": "นายธวัช เจริญศิลป์", "guardian_phone": "082-333-4455", "guardian_rel": "บิดา",
            "level": "ปวช.",
            "major1": "เทคโนโลยีสารสนเทศ",
            "major2": "ช่างอิเล็กทรอนิกส์",
            "quota": "โควตากิจกรรม/ความสามารถพิเศษ",
            "old_school": "โรงเรียนสตรีนนทบุรี",
            "old_province": "นนทบุรี",
            "gpa": 3.15,
            "referrer": "เพื่อน/รุ่นพี่",
            "status": "รอตรวจสอบ",
            "notes": "สมัครเข้ามาใหม่ รอเจ้าหน้าที่ตรวจเอกสาร",
            "student_id": None
        },
        {
            "id_prefix": "140990033445",
            "prefix": "นางสาว",
            "first_th": "พิมพ์ลดา",
            "last_th": "แก้วสว่าง",
            "first_en": "Pimlada",
            "last_en": "Kaewsawang",
            "gender": "หญิง",
            "birth": "2008-01-30",
            "phone": "082-999-1122",
            "email": "pimlada.k@yahoo.com",
            "address": "90/4", "moo": "2", "subdistrict": "ปากเกร็ด", "district": "ปากเกร็ด", "province": "นนทบุรี", "zip": "11120",
            "father": "นายชูชาติ แก้วสว่าง", "father_phone": "086-111-9988",
            "mother": "นางมาลี แก้วสว่าง", "mother_phone": "086-222-9988",
            "guardian": "นางมาลี แก้วสว่าง", "guardian_phone": "086-222-9988", "guardian_rel": "มารดา",
            "level": "ปวช.",
            "major1": "การบัญชี",
            "major2": "การตลาด",
            "quota": "โควตารับตรง/เรียนดี",
            "old_school": "โรงเรียนปากเกร็ด",
            "old_province": "นนทบุรี",
            "gpa": 3.88,
            "referrer": "ครูแนะแนว",
            "status": "เอกสารไม่สมบูรณ์",
            "notes": "ใบแสดงผลการเรียน (รบ.) ไม่ชัดเจน กรุณาถ่ายเอกสารหน้า-หลังแล้วอัปโหลดใหม่",
            "student_id": None
        },
        {
            "id_prefix": "150010077889",
            "prefix": "นาย",
            "first_th": "ภานุพงศ์",
            "last_th": "มุ่งมั่นพัฒนา",
            "first_en": "Panupong",
            "last_en": "Mungmun",
            "gender": "ชาย",
            "birth": "2006-03-12",
            "phone": "091-777-8899",
            "email": "panupong.m@gmail.com",
            "address": "14/2", "moo": "8", "subdistrict": "บางบัวทอง", "district": "บางบัวทอง", "province": "นนทบุรี", "zip": "11110",
            "father": "นายประสิทธิ์ มุ่งมั่นพัฒนา", "father_phone": "083-444-5566",
            "mother": "นางวรรณา มุ่งมั่นพัฒนา", "mother_phone": "083-777-8899",
            "guardian": "นายประสิทธิ์ มุ่งมั่นพัฒนา", "guardian_phone": "083-444-5566", "guardian_rel": "บิดา",
            "level": "ปวส.",
            "major1": "เทคนิคเครื่องกล",
            "major2": "ไฟฟ้า",
            "quota": "สอบคัดเลือกทั่วไป",
            "old_school": "วิทยาลัยเทคนิคนนทบุรี",
            "old_province": "นนทบุรี",
            "gpa": 2.95,
            "referrer": "ป้ายประชาสัมพันธ์",
            "status": "ผ่านการคัดเลือก",
            "notes": "ตรวจเอกสารผ่านแล้ว ยืนยันสิทธิ์เข้ามอบตัวได้ในวันที่กำหนด",
            "student_id": None
        },
        {
            "id_prefix": "160020088990",
            "prefix": "นางสาว",
            "first_th": "อรปรียา",
            "last_th": "โชคอำนวย",
            "first_en": "Onpreeya",
            "last_en": "Chokamnuay",
            "gender": "หญิง",
            "birth": "2008-09-25",
            "phone": "084-555-1234",
            "email": "onpreeya.c@gmail.com",
            "address": "205/3", "moo": "4", "subdistrict": "ไทรน้อย", "district": "ไทรน้อย", "province": "นนทบุรี", "zip": "11150",
            "father": "นายเกรียงไกร โชคอำนวย", "father_phone": "087-222-3311",
            "mother": "นางดวงใจ โชคอำนวย", "mother_phone": "087-444-5522",
            "guardian": "นางดวงใจ โชคอำนวย", "guardian_phone": "087-444-5522", "guardian_rel": "มารดา",
            "level": "ปวช.",
            "major1": "การตลาด",
            "major2": "การบัญชี",
            "quota": "โควตารับตรง/เรียนดี",
            "old_school": "โรงเรียนไทรน้อย",
            "old_province": "นนทบุรี",
            "gpa": 3.60,
            "referrer": "ครูแนะแนว",
            "status": "รอตรวจสอบ",
            "notes": "ยื่นใบสมัครออนไลน์สมบูรณ์",
            "student_id": None
        }
    ]

    for s in samples:
        cid = make_valid_thai_id(s["id_prefix"])
        cursor.execute("""
        INSERT INTO applicants (
            citizen_id, prefix_th, first_name_th, last_name_th, first_name_en, last_name_en,
            gender, birth_date, phone, email, address_no, moo, subdistrict, district, province, postal_code,
            father_name, father_phone, mother_name, mother_phone, guardian_name, guardian_phone, guardian_relation,
            education_level, first_choice_major, second_choice_major, quota_type,
            old_school, old_school_province, gpa, referrer, status, admin_notes, student_id
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """, (
            cid, s["prefix"], s["first_th"], s["last_th"], s["first_en"], s["last_en"],
            s["gender"], s["birth"], s["phone"], s["email"], s["address"], s["moo"], s["subdistrict"], s["district"], s["province"], s["zip"],
            s["father"], s["father_phone"], s["mother"], s["mother_phone"], s["guardian"], s["guardian_phone"], s["guardian_rel"],
            s["level"], s["major1"], s["major2"], s["quota"],
            s["old_school"], s["old_province"], s["gpa"], s["referrer"], s["status"], s["notes"], s["student_id"]
        ))
        app_id = cursor.lastrowid

        # Add sample documents
        doc_types = [
            ("photo", f"photo_{cid}.jpg", "ถูกต้อง" if s["status"] in ["ผ่านการคัดเลือก", "มอบตัวแล้ว"] else ("ต้องแก้ไข" if s["status"] == "เอกสารไม่สมบูรณ์" else "รอตรวจ")),
            ("id_card", f"id_card_{cid}.pdf", "ถูกต้อง" if s["status"] in ["ผ่านการคัดเลือก", "มอบตัวแล้ว"] else "รอตรวจ"),
            ("house_reg", f"house_reg_{cid}.pdf", "ถูกต้อง" if s["status"] in ["ผ่านการคัดเลือก", "มอบตัวแล้ว"] else "รอตรวจ"),
            ("transcript", f"transcript_{cid}.pdf", "ต้องแก้ไข" if s["status"] == "เอกสารไม่สมบูรณ์" else ("ถูกต้อง" if s["status"] in ["ผ่านการคัดเลือก", "มอบตัวแล้ว"] else "รอตรวจ"))
        ]

        for dtype, fname, dstat in doc_types:
            cursor.execute("""
            INSERT INTO documents (applicant_id, doc_type, filename, file_path, status, comment)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (app_id, dtype, fname, f"/static/uploads/{fname}", dstat, "ภาพไม่ชัดเจน กรุณาอัปโหลดใหม่" if dstat == "ต้องแก้ไข" else "ตรวจสอบเรียบร้อย"))

        # Add enrollment if status is 'มอบตัวแล้ว'
        if s["status"] == "มอบตัวแล้ว" and s["student_id"]:
            cursor.execute("""
            INSERT INTO enrollments (applicant_id, student_id, guardian_name, guardian_phone, guardian_relation, witness_name, enrolled_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (app_id, s["student_id"], s["guardian"], s["guardian_phone"], s["guardian_rel"], "อาจารย์สมศักดิ์ มั่นใจ (นายทะเบียน)", "2026-05-10"))

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully with sample data!")
