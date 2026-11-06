"""
Export Service for Standardized ศธ.02 (Ministry of Education) Format
Generates Excel (.xlsx) and CSV (.csv with UTF-8 BOM) for direct import into registry databases.
"""
import io
import csv
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Mapping of Vocational Major Names to Official Department of Vocational Education (สอศ.) Codes
MAJOR_CODES = {
    # ปวช. (รหัสขึ้นต้น 2xxxx)
    "สาขาเทคโนโลยีสารสนเทศ": "20901",
    "เทคโนโลยีสารสนเทศ": "20901",
    "สาขาการบัญชี": "20201",
    "การบัญชี": "20201",
    "สาขาเทคโนโลยีธุรกิจดิจิทัล": "20204",
    "เทคโนโลยีธุรกิจดิจิทัล": "20204",
    "สาขาการตลาด": "20202",
    "การตลาด": "20202",
    "สาขาไฟฟ้ากำลัง": "20104",
    "ไฟฟ้ากำลัง": "20104",
    "สาขาอิเล็กทรอนิกส์": "20105",
    "อิเล็กทรอนิกส์": "20105",
    "สาขาเทคนิคคอมพิวเตอร์": "20128",
    "เทคนิคคอมพิวเตอร์": "20128",
    "สาขาเทคนิคการผลิต": "20102",
    "เทคนิคการผลิต": "20102",
    "สาขาซ่อมบำรุงอุตสาหกรรม": "20107",
    "ซ่อมบำรุงอุตสาหกรรม": "20107",
    "สาขายานยนต์": "20101",
    "ยานยนต์": "20101",
    "สาขาเมคคาทรอนิกส์": "20127",
    "เมคคาทรอนิกส์": "20127",
    "สาชาเมคคาทรอนิกส์": "20127",

    # ปวส. (รหัสขึ้นต้น 3xxxx)
    "สาขาเทคโนโลยีคอมพิวเตอร์": "30128",
    "เทคโนโลยีคอมพิวเตอร์": "30128",

    # เข้ากันได้กับข้อมูลตัวอย่างเดิม
    "ช่างยนต์": "20101",
    "ช่างกลโรงงาน": "20102",
    "ช่างเชื่อมโลหะ": "20103",
    "ช่างไฟฟ้ากำลัง": "20104",
    "ช่างอิเล็กทรอนิกส์": "20105",
    "คอมพิวเตอร์ธุรกิจ": "20204",
    "เทคนิคเครื่องกล": "30101",
    "ไฟฟ้า": "30104",
    "การจัดการโลจิสติกส์": "30214",
}

def resolve_major_code(level: str, major_name: str) -> str:
    """Resolve standardized 5-digit Vocational Curriculum code for ศธ.02 according to educational level"""
    level = (level or "").strip()
    name = (major_name or "").strip().replace("สาขา", "").replace("สาชา", "").strip()
    is_pvs = "ปวส" in level
    prefix = "3" if is_pvs else "2"

    if "สารสนเทศ" in name:
        return f"{prefix}0901"
    elif "บัญชี" in name:
        return f"{prefix}0201"
    elif "ธุรกิจดิจิทัล" in name or "คอมพิวเตอร์ธุรกิจ" in name:
        return f"{prefix}0204"
    elif "ตลาด" in name:
        return f"{prefix}0202"
    elif "ไฟฟ้า" in name:
        return f"{prefix}0104"
    elif "อิเล็กทรอนิกส์" in name:
        return f"{prefix}0105"
    elif "เทคนิคคอมพิวเตอร์" in name:
        return "20128"
    elif "เทคโนโลยีคอมพิวเตอร์" in name:
        return "30128"
    elif "คอมพิวเตอร์" in name:
        return f"{prefix}0128"
    elif "การผลิต" in name or "ช่างกล" in name:
        return f"{prefix}0102"
    elif "ซ่อมบำรุง" in name:
        return f"{prefix}0107"
    elif "ยานยนต์" in name or "ช่างยนต์" in name or "เครื่องกล" in name:
        return f"{prefix}0101"
    elif "เมคคาทรอนิกส์" in name:
        return f"{prefix}0127"
    elif "โลจิสติกส์" in name:
        return f"{prefix}0214"

    return MAJOR_CODES.get(major_name, MAJOR_CODES.get(name, f"{prefix}0101"))

def format_thai_date(date_str):
    """Convert YYYY-MM-DD to DD/MM/YYYY (พ.ศ.) for ศธ.02"""
    if not date_str:
        return ""
    try:
        parts = date_str.split("-")
        if len(parts) == 3:
            year_be = int(parts[0]) + 543
            return f"{parts[2]}/{parts[1]}/{year_be}"
    except Exception:
        pass
    return date_str

def generate_std02_excel(applicants: list[dict]) -> bytes:
    """Generate professional Excel workbook conforming to ศธ.02 specifications"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ศธ.02_ข้อมูลนักเรียนนักศึกษา"
    ws.views.sheetView[0].showGridLines = True

    # Title Block
    ws.merge_cells("A1:AG1")
    title_cell = ws["A1"]
    title_cell.value = "แบบบันทึกข้อมูลประวัตินักเรียน นักศึกษาเข้าใหม่เพื่อนำเข้าสู่ระบบ ศธ.02 (งานทะเบียนและประมวลผล)"
    title_cell.font = Font(name="TH Sarabun New", size=16, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 35

    # Subtitle Block
    ws.merge_cells("A2:AG2")
    sub_cell = ws["A2"]
    sub_cell.value = f"ปีการศึกษา 2568 | ข้อมูล ณ วันที่ส่งออก: {datetime.now().strftime('%d/%m/%Y %H:%M')} | จำนวนผู้สมัครทั้งหมด: {len(applicants)} คน"
    sub_cell.font = Font(name="TH Sarabun New", size=12, italic=True, color="1E3A8A")
    sub_cell.fill = PatternFill(start_color="E0E7FF", end_color="E0E7FF", fill_type="solid")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22

    # Column Headers
    headers = [
        "ลำดับ",
        "เลขประจำตัวนักศึกษา (ศธ.02)",
        "เลขประจำตัวประชาชน (13 หลัก)",
        "คำนำหน้า",
        "ชื่อ (ภาษาไทย)",
        "นามสกุล (ภาษาไทย)",
        "ชื่อ (อังกฤษ)",
        "นามสกุล (อังกฤษ)",
        "เพศ",
        "วันเดือนปีเกิด (พ.ศ.)",
        "สัญชาติ",
        "ศาสนา",
        "ระดับการศึกษา",
        "รหัสสาขาวิชา",
        "สาขาวิชา (อันดับ 1)",
        "สาขาวิชา (อันดับ 2)",
        "ประเภทโควตา",
        "ผลการเรียนเฉลี่ย (GPA)",
        "โรงเรียนเดิม",
        "จังหวัดโรงเรียนเดิม",
        "เบอร์โทรศัพท์ผู้สมัคร",
        "อีเมล",
        "บ้านเลขที่",
        "หมู่ที่",
        "ตำบล/แขวง",
        "อำเภอ/เขต",
        "จังหวัด",
        "รหัสไปรษณีย์",
        "ชื่อ-สกุล บิดา",
        "ชื่อ-สกุล มารดา",
        "ชื่อ-สกุล ผู้ปกครอง",
        "ความสัมพันธ์ผู้ปกครอง",
        "สถานะในระบบรับสมัคร"
    ]

    header_font = Font(name="TH Sarabun New", size=12, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    ws.row_dimensions[3].height = 30
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border

    # Data Rows
    row_font = Font(name="TH Sarabun New", size=11)
    stripe_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    for i, app in enumerate(applicants, 1):
        row_num = i + 3
        ws.row_dimensions[row_num].height = 22
        fill = stripe_fill if i % 2 == 0 else white_fill

        major_code = resolve_major_code(app.get("education_level", ""), app.get("first_choice_major", ""))
        birth_thai = format_thai_date(app.get("birth_date", ""))

        row_values = [
            i,
            app.get("student_id") or "-",
            app.get("citizen_id", ""),
            app.get("prefix_th", ""),
            app.get("first_name_th", ""),
            app.get("last_name_th", ""),
            app.get("first_name_en") or "",
            app.get("last_name_en") or "",
            app.get("gender", ""),
            birth_thai,
            app.get("nationality", "ไทย"),
            app.get("religion", "พุทธ"),
            app.get("education_level", ""),
            major_code,
            app.get("first_choice_major", ""),
            app.get("second_choice_major") or "-",
            app.get("quota_type", ""),
            f"{float(app.get('gpa', 0)):.2f}",
            app.get("old_school", ""),
            app.get("old_school_province", ""),
            app.get("phone", ""),
            app.get("email") or "",
            app.get("address_no", ""),
            app.get("moo") or "-",
            app.get("subdistrict", ""),
            app.get("district", ""),
            app.get("province", ""),
            app.get("postal_code", ""),
            app.get("father_name") or "-",
            app.get("mother_name") or "-",
            app.get("guardian_name") or "-",
            app.get("guardian_relation") or "-",
            app.get("status", "")
        ]

        for col_idx, val in enumerate(row_values, 1):
            cell = ws.cell(row=row_num, column=col_idx, value=val)
            cell.font = row_font
            cell.fill = fill
            cell.border = thin_border

            # Specific column alignments
            if col_idx in [1, 2, 3, 9, 10, 13, 14, 18, 28, 33]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in [17, 21]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # Auto-fit column widths
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.row < 3:
                continue
            val_str = str(cell.value or "")
            # Thai characters approximation width
            length = len(val_str)
            if length > max_len:
                max_len = length
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()

def generate_std02_csv(applicants: list[dict]) -> bytes:
    """Generate CSV with UTF-8 BOM for Thai Windows Excel compatibility"""
    output = io.StringIO()
    # Write UTF-8 BOM is done when encoding
    headers = [
        "ลำดับ", "เลขประจำตัวนักศึกษา", "เลขประจำตัวประชาชน", "คำนำหน้า", "ชื่อ", "นามสกุล",
        "เพศ", "วันเกิด", "ระดับการศึกษา", "รหัสสาขาวิชา", "สาขาวิชา", "เกรดเฉลี่ย",
        "โรงเรียนเดิม", "จังหวัดโรงเรียนเดิม", "เบอร์โทรศัพท์", "ชื่อผู้ปกครอง",
        "เบอร์โทรผู้ปกครอง", "ความสัมพันธ์", "สถานะ"
    ]
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()

    for i, app in enumerate(applicants, 1):
        major_code = resolve_major_code(app.get("education_level", ""), app.get("first_choice_major", ""))
        birth_thai = format_thai_date(app.get("birth_date", ""))
        writer.writerow({
            "ลำดับ": i,
            "เลขประจำตัวนักศึกษา": app.get("student_id") or "",
            "เลขประจำตัวประชาชน": f"'{app.get('citizen_id', '')}",  # quote to prevent excel scientific notation
            "คำนำหน้า": app.get("prefix_th", ""),
            "ชื่อ": app.get("first_name_th", ""),
            "นามสกุล": app.get("last_name_th", ""),
            "เพศ": app.get("gender", ""),
            "วันเกิด": birth_thai,
            "ระดับการศึกษา": app.get("education_level", ""),
            "รหัสสาขาวิชา": major_code,
            "สาขาวิชา": app.get("first_choice_major", ""),
            "เกรดเฉลี่ย": f"{float(app.get('gpa', 0)):.2f}",
            "โรงเรียนเดิม": app.get("old_school", ""),
            "จังหวัดโรงเรียนเดิม": app.get("old_school_province", ""),
            "เบอร์โทรศัพท์": app.get("phone", ""),
            "ชื่อผู้ปกครอง": app.get("guardian_name") or "",
            "เบอร์โทรผู้ปกครอง": app.get("guardian_phone") or "",
            "ความสัมพันธ์": app.get("guardian_relation") or "",
            "สถานะ": app.get("status", "")
        })

    return output.getvalue().encode("utf-8-sig")
