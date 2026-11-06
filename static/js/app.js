/**
 * Student Admission System - Interactive Frontend Logic
 * Dual-Mode Engine: Seamlessly runs on FastAPI backend OR 100% Client-Side on GitHub Pages!
 */

let majorsChartInstance = null;
let levelsChartInstance = null;
let referrersChartInstance = null;
let allApplicants = [];
let currentApplicantInView = null;
let isStaticMode = (window.location.protocol === "file:" || window.location.hostname.includes("github.io"));

// Vocational Majors Definition (11 Majors for ปวช. and 11 Majors for ปวส.)
const MAJORS_BY_LEVEL = {
    "ปวช.": [
        "สาขาเทคโนโลยีสารสนเทศ",
        "สาขาการบัญชี",
        "สาขาเทคโนโลยีธุรกิจดิจิทัล",
        "สาขาการตลาด",
        "สาขาไฟฟ้ากำลัง",
        "สาขาอิเล็กทรอนิกส์",
        "สาขาเทคนิคคอมพิวเตอร์",
        "สาขาเทคนิคการผลิต",
        "สาขาซ่อมบำรุงอุตสาหกรรม",
        "สาขายานยนต์",
        "สาขาเมคคาทรอนิกส์"
    ],
    "ปวส.": [
        "สาขาเทคโนโลยีสารสนเทศ",
        "สาขาการบัญชี",
        "สาขาเทคโนโลยีธุรกิจดิจิทัล",
        "สาขาการตลาด",
        "สาขาไฟฟ้ากำลัง",
        "สาขาอิเล็กทรอนิกส์",
        "สาขาเทคโนโลยีคอมพิวเตอร์",
        "สาขาเทคนิคการผลิต",
        "สาขาซ่อมบำรุงอุตสาหกรรม",
        "สาขายานยนต์",
        "สาขาเมคคาทรอนิกส์"
    ]
};

// Initial Seed Data for GitHub Pages LocalStorage
const INITIAL_SAMPLE_DATA = [
    {
        id: 1,
        citizen_id: "1100701234561",
        prefix_th: "นาย",
        first_name_th: "สมชาย",
        last_name_th: "ใจดีมั่นคง",
        gender: "ชาย",
        birth_date: "2008-05-14",
        education_level: "ปวช.",
        first_choice_major: "สาขายานยนต์",
        second_choice_major: "สาขาไฟฟ้ากำลัง",
        quota_type: "โควตารับตรง/เรียนดี",
        gpa: 3.75,
        phone: "081-234-5678",
        email: "somchai.j@gmail.com",
        address_no: "123/45", moo: "3", subdistrict: "บางเขน", district: "เมือง", province: "นนทบุรี", postal_code: "11000",
        old_school: "โรงเรียนนนทบุรีพิทยาคม", old_school_province: "นนทบุรี",
        father_name: "นายวิชัย ใจดีมั่นคง", mother_name: "นางสมศรี ใจดีมั่นคง",
        guardian_name: "นายวิชัย ใจดีมั่นคง", guardian_relation: "บิดา", guardian_phone: "089-111-2233",
        status: "ผ่านการคัดเลือก",
        admin_notes: "เอกสารครบถ้วน ผลการเรียนดีเด่น มีสิทธิ์มอบตัว",
        student_id: null,
        referrer: "ครูแนะแนว",
        documents: [
            { doc_type: "photo", filename: "photo_1100701234561.jpg", status: "ถูกต้อง", comment: "ตรวจสอบเรียบร้อย" },
            { doc_type: "id_card", filename: "id_card_1100701234561.pdf", status: "ถูกต้อง", comment: "ตรวจสอบเรียบร้อย" },
            { doc_type: "house_reg", filename: "house_reg_1100701234561.pdf", status: "ถูกต้อง", comment: "ตรวจสอบเรียบร้อย" },
            { doc_type: "transcript", filename: "transcript_1100701234561.pdf", status: "ถูกต้อง", comment: "ตรวจสอบเรียบร้อย" }
        ]
    },
    {
        id: 2,
        citizen_id: "1200900456788",
        prefix_th: "นางสาว",
        first_name_th: "กนกพร",
        last_name_th: "รักการเรียน",
        gender: "หญิง",
        birth_date: "2006-11-20",
        education_level: "ปวส.",
        first_choice_major: "สาขาเทคโนโลยีธุรกิจดิจิทัล",
        second_choice_major: "สาขาการบัญชี",
        quota_type: "สอบคัดเลือกทั่วไป",
        gpa: 3.42,
        phone: "089-876-5432",
        email: "kanokporn.r@gmail.com",
        address_no: "88/12", moo: "1", subdistrict: "คลองหนึ่ง", district: "คลองหลวง", province: "ปทุมธานี", postal_code: "12120",
        old_school: "วิทยาลัยอาชีวศึกษาปทุมธานี", old_school_province: "ปทุมธานี",
        father_name: "นายประเสริฐ รักการเรียน", mother_name: "นางสุจิตรา รักการเรียน",
        guardian_name: "นางสุจิตรา รักการเรียน", guardian_relation: "มารดา", guardian_phone: "081-555-6677",
        status: "มอบตัวแล้ว",
        admin_notes: "มอบตัวและชำระค่าธรรมเนียมเรียบร้อยแล้ว",
        student_id: "68302040001",
        referrer: "Facebook/TikTok",
        documents: [
            { doc_type: "photo", filename: "photo_1200900456788.jpg", status: "ถูกต้อง", comment: "ตรวจสอบเรียบร้อย" },
            { doc_type: "id_card", filename: "id_card_1200900456788.pdf", status: "ถูกต้อง", comment: "ตรวจสอบเรียบร้อย" },
            { doc_type: "house_reg", filename: "house_reg_1200900456788.pdf", status: "ถูกต้อง", comment: "ตรวจสอบเรียบร้อย" },
            { doc_type: "transcript", filename: "transcript_1200900456788.pdf", status: "ถูกต้อง", comment: "ตรวจสอบเรียบร้อย" }
        ]
    },
    {
        id: 3,
        citizen_id: "1409900334451",
        prefix_th: "นางสาว",
        first_name_th: "พิมพ์ลดา",
        last_name_th: "แก้วสว่าง",
        gender: "หญิง",
        birth_date: "2008-01-30",
        education_level: "ปวช.",
        first_choice_major: "สาขาการบัญชี",
        second_choice_major: "สาขาการตลาด",
        quota_type: "โควตารับตรง/เรียนดี",
        gpa: 3.88,
        phone: "082-999-1122",
        email: "pimlada.k@yahoo.com",
        address_no: "90/4", moo: "2", subdistrict: "ปากเกร็ด", district: "ปากเกร็ด", province: "นนทบุรี", postal_code: "11120",
        old_school: "โรงเรียนปากเกร็ด", old_school_province: "นนทบุรี",
        father_name: "นายชูชาติ แก้วสว่าง", mother_name: "นางมาลี แก้วสว่าง",
        guardian_name: "นางมาลี แก้วสว่าง", guardian_relation: "มารดา", guardian_phone: "086-222-9988",
        status: "เอกสารไม่สมบูรณ์",
        admin_notes: "ใบแสดงผลการเรียน (รบ.) ไม่ชัดเจน กรุณาถ่ายเอกสารหน้า-หลังแล้วอัปโหลดใหม่",
        student_id: null,
        referrer: "ครูแนะแนว",
        documents: [
            { doc_type: "photo", filename: "photo_1409900334451.jpg", status: "รอตรวจ", comment: "รอตรวจ" },
            { doc_type: "id_card", filename: "id_card_1409900334451.pdf", status: "ถูกต้อง", comment: "ตรวจแล้ว" },
            { doc_type: "house_reg", filename: "house_reg_1409900334451.pdf", status: "ถูกต้อง", comment: "ตรวจแล้ว" },
            { doc_type: "transcript", filename: "transcript_1409900334451.pdf", status: "ต้องแก้ไข", comment: "ภาพไม่ชัดเจน" }
        ]
    }
];

function getLocalData() {
    let data = localStorage.getItem("admission_applicants_data");
    if (!data) {
        localStorage.setItem("admission_applicants_data", JSON.stringify(INITIAL_SAMPLE_DATA));
        return INITIAL_SAMPLE_DATA;
    }
    try {
        return JSON.parse(data);
    } catch(e) {
        return INITIAL_SAMPLE_DATA;
    }
}

function saveLocalData(data) {
    localStorage.setItem("admission_applicants_data", JSON.stringify(data));
}

document.addEventListener("DOMContentLoaded", () => {
    updateMajorOptions();
    updateDateTime();
    setInterval(updateDateTime, 1000);
    loadAdminDashboard();
});

function updateDateTime() {
    const el = document.getElementById("currentDateTime");
    if (el) {
        const now = new Date();
        el.textContent = now.toLocaleDateString("th-TH", {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });
    }
}

// --------------------------------------------------------------------------
// Navigation & Tabs
// --------------------------------------------------------------------------
function switchTab(tabId) {
    const tabs = ["apply", "status", "admin", "std02"];
    tabs.forEach(t => {
        const section = document.getElementById(`tab-${t}`);
        const btn = document.getElementById(`tab-${t}-btn`);
        if (section && btn) {
            if (t === tabId) {
                section.classList.remove("hidden");
                btn.classList.add("active");
            } else {
                section.classList.add("hidden");
                btn.classList.remove("active");
            }
        }
    });

    if (tabId === "admin") {
        loadAdminDashboard();
    }

    if (window.lucide) {
        lucide.createIcons();
    }
}

// --------------------------------------------------------------------------
// Form Logic & Real-Time Validation
// --------------------------------------------------------------------------
function updateMajorOptions() {
    const level = document.getElementById("educationLevel").value;
    const major1 = document.getElementById("firstChoiceMajor");
    const major2 = document.getElementById("secondChoiceMajor");

    const list = MAJORS_BY_LEVEL[level] || [];

    major1.innerHTML = "";
    major2.innerHTML = '<option value="">-- ไม่ประสงค์ระบุอันดับ 2 --</option>';

    list.forEach(m => {
        const opt1 = document.createElement("option");
        opt1.value = m;
        opt1.textContent = m;
        major1.appendChild(opt1);

        const opt2 = document.createElement("option");
        opt2.value = m;
        opt2.textContent = m;
        major2.appendChild(opt2);
    });
}

function validateThaiCitizenId(idStr) {
    const digits = idStr.replace(/\D/g, "");
    if (digits.length !== 13) return false;

    let sum = 0;
    for (let i = 0; i < 12; i++) {
        sum += parseInt(digits.charAt(i), 10) * (13 - i);
    }
    const checkDigit = (11 - (sum % 11)) % 10;
    return checkDigit === parseInt(digits.charAt(12), 10);
}

function handleCitizenIdInput(input) {
    let val = input.value.replace(/\D/g, "");
    if (val.length > 13) val = val.slice(0, 13);

    let formatted = "";
    if (val.length > 0) formatted += val.substring(0, 1);
    if (val.length > 1) formatted += "-" + val.substring(1, 5);
    if (val.length > 5) formatted += "-" + val.substring(5, 10);
    if (val.length > 10) formatted += "-" + val.substring(10, 12);
    if (val.length > 12) formatted += "-" + val.substring(12, 13);

    input.value = formatted;

    const badge = document.getElementById("citizenIdValidationBadge");
    if (!badge) return;

    if (val.length === 0) {
        badge.innerHTML = `<i data-lucide="info" class="w-4 h-4"></i><span>กรุณากรอกเลขประจำตัวประชาชน 13 หลัก</span>`;
        badge.className = "mt-2 text-xs flex items-center gap-1.5 text-slate-500";
    } else if (val.length < 13) {
        badge.innerHTML = `<i data-lucide="clock" class="w-4 h-4 text-amber-500"></i><span class="text-amber-700">กำลังกรอก... (ระบุแล้ว ${val.length}/13 หลัก)</span>`;
        badge.className = "mt-2 text-xs flex items-center gap-1.5";
    } else {
        const isValid = validateThaiCitizenId(val);
        if (isValid) {
            badge.innerHTML = `<i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-600"></i><span class="text-emerald-700 font-bold">เลขประจำตัวประชาชนถูกต้องตามสูตรคำนวณ (Checksum Valid)</span>`;
            badge.className = "mt-2 text-xs flex items-center gap-1.5";
        } else {
            badge.innerHTML = `<i data-lucide="alert-circle" class="w-4 h-4 text-rose-600"></i><span class="text-rose-700 font-bold">เลขประจำตัวประชาชนไม่ถูกต้องตามสูตร Modulo 11 กรุณาตรวจสอบอีกครั้ง</span>`;
            badge.className = "mt-2 text-xs flex items-center gap-1.5";
        }
    }
    if (window.lucide) lucide.createIcons();
}

function handlePhoneInput(input) {
    let val = input.value.replace(/\D/g, "");
    if (val.length > 10) val = val.slice(0, 10);

    let formatted = "";
    if (val.length > 0) formatted += val.substring(0, 3);
    if (val.length > 3) formatted += "-" + val.substring(3, 6);
    if (val.length > 6) formatted += "-" + val.substring(6, 10);

    input.value = formatted;
}

async function handleRegistrationSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = document.getElementById("submitBtn");

    const citizenInput = document.getElementById("citizenIdInput");
    const rawCid = citizenInput.value.replace(/\D/g, "");

    if (!validateThaiCitizenId(rawCid)) {
        alert("ขออภัย: เลขประจำตัวประชาชน 13 หลักไม่ถูกต้องตามสูตรคำนวณ กรุณาตรวจสอบตัวเลขอีกครั้ง");
        citizenInput.focus();
        return;
    }

    const formData = new FormData(form);
    const dataObj = {};
    formData.forEach((value, key) => {
        dataObj[key] = value;
    });
    dataObj.citizen_id = rawCid;

    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></span> กำลังบันทึกข้อมูล...`;

    // Try backend if not static
    if (!isStaticMode) {
        try {
            const resp = await fetch("/api/applicants/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dataObj)
            });
            if (resp.ok) {
                showSuccessModal(citizenInput.value, `${dataObj.education_level} - ${dataObj.first_choice_major}`);
                form.reset();
                updateMajorOptions();
                handleCitizenIdInput(citizenInput);
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<i data-lucide="send" class="w-4 h-4"></i><span>ส่งใบสมัครเข้าศึกษาต่อ</span>`;
                return;
            }
        } catch(e) {
            isStaticMode = true; // fallback to client-side
        }
    }

    // Static / LocalStorage fallback
    let list = getLocalData();
    if (list.some(a => a.citizen_id === rawCid)) {
        alert("เลขประจำตัวประชาชนนี้ได้ทำการสมัครในระบบแล้ว กรุณาตรวจสอบสถานะในแท็บที่ 2");
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i data-lucide="send" class="w-4 h-4"></i><span>ส่งใบสมัครเข้าศึกษาต่อ</span>`;
        return;
    }

    dataObj.id = list.length + 1;
    dataObj.status = "รอตรวจสอบ";
    dataObj.admin_notes = "ได้รับใบสมัครเข้าสู่ระบบแล้ว รอเจ้าหน้าที่ตรวจสอบเอกสาร";
    dataObj.student_id = null;
    dataObj.documents = [
        { doc_type: "photo", filename: `photo_${rawCid}.jpg`, status: "รอตรวจ", comment: "รอตรวจ" },
        { doc_type: "id_card", filename: `id_card_${rawCid}.pdf`, status: "รอตรวจ", comment: "รอตรวจ" },
        { doc_type: "house_reg", filename: `house_reg_${rawCid}.pdf`, status: "รอตรวจ", comment: "รอตรวจ" },
        { doc_type: "transcript", filename: `transcript_${rawCid}.pdf`, status: "รอตรวจ", comment: "รอตรวจ" }
    ];

    list.unshift(dataObj);
    saveLocalData(list);

    showSuccessModal(citizenInput.value, `${dataObj.education_level} - ${dataObj.first_choice_major}`);
    form.reset();
    updateMajorOptions();
    handleCitizenIdInput(citizenInput);

    submitBtn.disabled = false;
    submitBtn.innerHTML = `<i data-lucide="send" class="w-4 h-4"></i><span>ส่งใบสมัครเข้าศึกษาต่อ</span>`;
    if (window.lucide) lucide.createIcons();
}

function showSuccessModal(cid, major) {
    document.getElementById("successCitizenId").textContent = cid;
    document.getElementById("successMajor").textContent = major;
    document.getElementById("successModal").classList.remove("hidden");
}

function closeSuccessModal() {
    document.getElementById("successModal").classList.add("hidden");
}

function goToStatusPageFromSuccess() {
    closeSuccessModal();
    const cid = document.getElementById("successCitizenId").textContent;
    switchTab("status");
    document.getElementById("statusSearchCitizenId").value = cid;
    searchApplicantStatus();
}

// --------------------------------------------------------------------------
// Status Tracker Logic
// --------------------------------------------------------------------------
function quickCheck(cid) {
    document.getElementById("statusSearchCitizenId").value = cid;
    handleCitizenIdInput(document.getElementById("statusSearchCitizenId"));
    searchApplicantStatus();
}

async function searchApplicantStatus() {
    const input = document.getElementById("statusSearchCitizenId");
    const rawCid = input.value.replace(/\D/g, "");

    if (rawCid.length !== 13) {
        alert("กรุณากรอกเลขประจำตัวประชาชน 13 หลักให้ครบถ้วน");
        return;
    }

    if (!isStaticMode) {
        try {
            const resp = await fetch(`/api/applicants/status/${rawCid}`);
            if (resp.ok) {
                const data = await resp.json();
                renderApplicantStatus(data);
                return;
            }
        } catch(e) {
            isStaticMode = true;
        }
    }

    // Static mode search
    const list = getLocalData();
    const item = list.find(a => a.citizen_id === rawCid);
    if (!item) {
        alert("ไม่พบข้อมูลผู้สมัครที่ใช้เลขบัตรประชาชนนี้ กรุณาตรวจสอบหรือทำการยื่นใบสมัครใหม่");
        document.getElementById("statusResultContainer").classList.add("hidden");
        return;
    }
    renderApplicantStatus(item);
}

function renderApplicantStatus(data) {
    currentApplicantInView = data;
    const container = document.getElementById("statusResultContainer");
    container.classList.remove("hidden");

    document.getElementById("resApplicantName").textContent = `${data.prefix_th}${data.first_name_th} ${data.last_name_th}`;
    document.getElementById("resCitizenId").textContent = data.citizen_id;

    const majorDisplay = data.first_choice_major.startsWith("สาขา") ? data.first_choice_major : `สาขา${data.first_choice_major}`;
    document.getElementById("resLevelMajor").textContent = `${data.education_level} ${majorDisplay}`;

    // Status Badge
    const badgeEl = document.getElementById("resStatusBadge");
    const status = data.status;
    let badgeClass = "bg-blue-100 text-blue-800";
    if (status === "รอตรวจสอบ") badgeClass = "bg-amber-100 text-amber-800 border border-amber-300";
    else if (status === "เอกสารไม่สมบูรณ์") badgeClass = "bg-rose-100 text-rose-800 border border-rose-300";
    else if (status === "ผ่านการคัดเลือก") badgeClass = "bg-emerald-100 text-emerald-800 border border-emerald-300";
    else if (status === "มอบตัวแล้ว") badgeClass = "bg-purple-100 text-purple-800 border border-purple-300";

    badgeEl.innerHTML = `<span class="px-3 py-1 rounded-full text-xs font-bold ${badgeClass}">${status}</span>`;

    // Stepper logic
    const s1 = document.getElementById("stepCircle1");
    const s2 = document.getElementById("stepCircle2");
    const s3 = document.getElementById("stepCircle3");
    const s4 = document.getElementById("stepCircle4");
    const line = document.getElementById("stepperProgressLine");

    [s2, s3, s4].forEach(c => {
        c.className = "w-8 h-8 rounded-full bg-slate-200 text-slate-600 font-bold text-xs flex items-center justify-center mb-2 shadow";
    });

    if (status === "รอตรวจสอบ") {
        line.style.width = "25%";
        s2.className = "w-8 h-8 rounded-full bg-amber-500 text-white font-bold text-xs flex items-center justify-center mb-2 shadow animate-pulse";
        s2.textContent = "⏳";
    } else if (status === "เอกสารไม่สมบูรณ์") {
        line.style.width = "25%";
        s2.className = "w-8 h-8 rounded-full bg-rose-500 text-white font-bold text-xs flex items-center justify-center mb-2 shadow";
        s2.textContent = "✕";
    } else if (status === "ผ่านการคัดเลือก") {
        line.style.width = "65%";
        s2.className = "w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center mb-2 shadow";
        s2.textContent = "✓";
        s3.className = "w-8 h-8 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center mb-2 shadow";
        s3.textContent = "✓";
    } else if (status === "มอบตัวแล้ว") {
        line.style.width = "100%";
        [s2, s3, s4].forEach(c => {
            c.className = "w-8 h-8 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center mb-2 shadow";
            c.textContent = "✓";
        });
    }

    document.getElementById("resAdminNotes").textContent = data.admin_notes || "ไม่มีข้อความแจ้งเตือนเพิ่มเติม";

    // Dynamic Download Links (Static GitHub Pages vs Python Backend)
    const btnApp = document.getElementById("btnDownloadAppPdf");
    btnApp.href = isStaticMode ? `print-application.html?cid=${data.citizen_id}` : `/api/applicants/${data.citizen_id}/application-pdf`;

    const btnEnroll = document.getElementById("btnDownloadEnrollPdf");
    btnEnroll.href = isStaticMode ? `print-enrollment.html?cid=${data.citizen_id}` : `/api/applicants/${data.citizen_id}/enrollment-pdf`;

    if (status === "ผ่านการคัดเลือก" || status === "มอบตัวแล้ว") {
        btnEnroll.classList.remove("hidden");
    } else {
        btnEnroll.classList.add("hidden");
    }

    const btnReup = document.getElementById("btnReuploadDocs");
    if (status === "เอกสารไม่สมบูรณ์") {
        btnReup.classList.remove("hidden");
    } else {
        btnReup.classList.add("hidden");
    }

    // Documents List
    const docsContainer = document.getElementById("resDocumentsList");
    docsContainer.innerHTML = "";
    const docNames = {
        photo: "รูปถ่ายหน้าตรง 1.5 นิ้ว",
        id_card: "สำเนาบัตรประชาชน",
        house_reg: "สำเนาทะเบียนบ้าน",
        transcript: "ใบแสดงผลการเรียน (รบ.)"
    };

    (data.documents || []).forEach(doc => {
        const item = document.createElement("div");
        item.className = "p-3 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between";

        let statusText = doc.status;
        let badgeColor = "bg-blue-100 text-blue-700";
        if (doc.status === "ถูกต้อง") badgeColor = "bg-emerald-100 text-emerald-700";
        else if (doc.status === "ต้องแก้ไข") badgeColor = "bg-rose-100 text-rose-700";

        item.innerHTML = `
            <div>
                <div class="text-xs font-bold text-slate-800">${docNames[doc.doc_type] || doc.doc_type}</div>
                <div class="text-[11px] text-slate-500 font-mono mt-0.5 truncate">${doc.filename}</div>
            </div>
            <div class="mt-2 pt-2 border-t border-slate-200 flex justify-between items-center">
                <span class="px-2 py-0.5 text-[10px] font-bold rounded ${badgeColor}">${statusText}</span>
                <span class="text-[10px] text-slate-400">${doc.comment || ''}</span>
            </div>
        `;
        docsContainer.appendChild(item);
    });

    if (window.lucide) lucide.createIcons();
}

function openReuploadModal() {
    document.getElementById("reuploadModal").classList.remove("hidden");
}

function closeReuploadModal() {
    document.getElementById("reuploadModal").classList.add("hidden");
}

async function submitReupload() {
    if (!currentApplicantInView) return;
    const docType = document.getElementById("reuploadDocType").value;
    const fileInput = document.getElementById("reuploadFile");

    if (!fileInput.files || fileInput.files.length === 0) {
        alert("กรุณาเลือกไฟล์ที่ต้องการส่ง");
        return;
    }

    if (!isStaticMode) {
        try {
            const formData = new FormData();
            formData.append("applicant_id", currentApplicantInView.id);
            formData.append("doc_type", docType);
            formData.append("file", fileInput.files[0]);
            const resp = await fetch("/api/applicants/update-docs", { method: "POST", body: formData });
            if (resp.ok) {
                alert("อัปโหลดเอกสารแก้ไขเรียบร้อยแล้ว!");
                closeReuploadModal();
                searchApplicantStatus();
                return;
            }
        } catch(e) {
            isStaticMode = true;
        }
    }

    // Static mode
    let list = getLocalData();
    let app = list.find(a => a.citizen_id === currentApplicantInView.citizen_id);
    if (app) {
        app.status = "รอตรวจสอบ";
        app.admin_notes = "ผู้สมัครได้ส่งเอกสารแก้ไขเรียบร้อยแล้ว รอการตรวจซ้ำ";
        let doc = (app.documents || []).find(d => d.doc_type === docType);
        if (doc) {
            doc.status = "รอตรวจ";
            doc.comment = "อัปโหลดเอกสารแก้ไขใหม่แล้ว";
            doc.filename = fileInput.files[0].name;
        }
        saveLocalData(list);
    }
    alert("อัปโหลดเอกสารแก้ไขเรียบร้อยแล้ว!");
    closeReuploadModal();
    searchApplicantStatus();
}

// --------------------------------------------------------------------------
// Admin Dashboard Logic
// --------------------------------------------------------------------------
async function loadAdminDashboard() {
    let analytics = null;

    if (!isStaticMode) {
        try {
            const resAnalytics = await fetch("/api/admin/analytics");
            if (resAnalytics.ok) {
                analytics = await resAnalytics.json();
                const resApplicants = await fetch("/api/admin/applicants");
                allApplicants = await resApplicants.json();
            }
        } catch(e) {
            isStaticMode = true;
        }
    }

    if (!analytics) {
        // Calculate analytics client-side from LocalStorage
        allApplicants = getLocalData();
        const total = allApplicants.length;
        const pending = allApplicants.filter(a => a.status === "รอตรวจสอบ").length;
        const passed = allApplicants.filter(a => a.status === "ผ่านการคัดเลือก").length;
        const enrolled = allApplicants.filter(a => a.status === "มอบตัวแล้ว").length;

        const by_major = {};
        const by_level = {};
        const by_referrer = {};

        allApplicants.forEach(a => {
            by_major[a.first_choice_major] = (by_major[a.first_choice_major] || 0) + 1;
            by_level[a.education_level] = (by_level[a.education_level] || 0) + 1;
            by_referrer[a.referrer || "อื่นๆ"] = (by_referrer[a.referrer || "อื่นๆ"] || 0) + 1;
        });

        analytics = {
            total_applicants: total,
            pending_review: pending,
            passed: passed,
            enrolled: enrolled,
            by_major: by_major,
            by_level: by_level,
            by_referrer: by_referrer
        };
    }

    document.getElementById("statTotal").textContent = analytics.total_applicants;
    document.getElementById("statPending").textContent = analytics.pending_review;
    document.getElementById("statPassed").textContent = analytics.passed;
    document.getElementById("statEnrolled").textContent = analytics.enrolled;
    document.getElementById("pendingBadge").textContent = analytics.pending_review;

    renderAnalyticsCharts(analytics);
    filterApplicantsTable();
}

function renderAnalyticsCharts(data) {
    const ctxMajors = document.getElementById("majorsChart");
    if (ctxMajors) {
        if (majorsChartInstance) majorsChartInstance.destroy();
        majorsChartInstance = new Chart(ctxMajors, {
            type: "doughnut",
            data: {
                labels: Object.keys(data.by_major),
                datasets: [{
                    data: Object.values(data.by_major),
                    backgroundColor: [
                        "#2563eb", "#0284c7", "#059669", "#d97706", "#7c3aed", "#db2777", "#475569", "#14b8a6", "#f97316", "#84cc16", "#6366f1"
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "right", labels: { boxWidth: 10, font: { size: 10 } } } }
            }
        });
    }

    const ctxLevels = document.getElementById("levelsChart");
    if (ctxLevels) {
        if (levelsChartInstance) levelsChartInstance.destroy();
        levelsChartInstance = new Chart(ctxLevels, {
            type: "bar",
            data: {
                labels: Object.keys(data.by_level),
                datasets: [{
                    label: "จำนวนผู้สมัคร",
                    data: Object.values(data.by_level),
                    backgroundColor: ["#3b82f6", "#8b5cf6"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
            }
        });
    }

    const ctxRef = document.getElementById("referrersChart");
    if (ctxRef) {
        if (referrersChartInstance) referrersChartInstance.destroy();
        referrersChartInstance = new Chart(ctxRef, {
            type: "bar",
            data: {
                labels: Object.keys(data.by_referrer),
                datasets: [{
                    label: "ผู้สมัคร",
                    data: Object.values(data.by_referrer),
                    backgroundColor: "#10b981"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
            }
        });
    }
}

function filterApplicantsTable() {
    const search = (document.getElementById("adminSearchInput").value || "").toLowerCase();
    const level = document.getElementById("filterLevel").value;
    const status = document.getElementById("filterStatus").value;
    const filterMajorEl = document.getElementById("filterMajor");
    const majorKeyword = filterMajorEl ? filterMajorEl.value : "ALL";

    const tbody = document.getElementById("applicantsTableBody");
    tbody.innerHTML = "";

    const filtered = allApplicants.filter(a => {
        const matchSearch = (
            a.first_name_th.toLowerCase().includes(search) ||
            a.last_name_th.toLowerCase().includes(search) ||
            a.citizen_id.includes(search) ||
            (a.old_school || "").toLowerCase().includes(search) ||
            (a.student_id || "").includes(search)
        );
        const matchLevel = (level === "ALL" || a.education_level === level);
        const matchStatus = (status === "ALL" || a.status === status);
        const matchMajor = (majorKeyword === "ALL" || (a.first_choice_major || "").includes(majorKeyword));
        return matchSearch && matchLevel && matchStatus && matchMajor;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="p-6 text-center text-slate-400">ไม่พบข้อมูลตามเงื่อนไขที่เลือก</td></tr>`;
        return;
    }

    filtered.forEach((app, idx) => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-50 transition border-b border-slate-100";

        let badgeClass = "bg-blue-100 text-blue-800";
        if (app.status === "รอตรวจสอบ") badgeClass = "bg-amber-100 text-amber-800";
        else if (app.status === "เอกสารไม่สมบูรณ์") badgeClass = "bg-rose-100 text-rose-800";
        else if (app.status === "ผ่านการคัดเลือก") badgeClass = "bg-emerald-100 text-emerald-800";
        else if (app.status === "มอบตัวแล้ว") badgeClass = "bg-purple-100 text-purple-800";

        const printPdfLink = isStaticMode ? `print-application.html?cid=${app.citizen_id}` : `/api/applicants/${app.citizen_id}/application-pdf`;

        tr.innerHTML = `
            <td class="p-3.5 text-slate-400 font-mono">${idx + 1}</td>
            <td class="p-3.5">
                <div class="font-mono font-bold text-slate-900">${app.citizen_id}</div>
                <div class="text-[11px] text-blue-600 font-mono font-semibold">${app.student_id ? 'รหัส: ' + app.student_id : 'ยังไม่ออกรหัส'}</div>
            </td>
            <td class="p-3.5">
                <div class="font-bold text-slate-800">${app.prefix_th}${app.first_name_th} ${app.last_name_th}</div>
                <div class="text-[11px] text-slate-400">โทร: ${app.phone}</div>
            </td>
            <td class="p-3.5">
                <span class="inline-block px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-bold mr-1">${app.education_level}</span>
                <span class="font-semibold text-slate-800">${app.first_choice_major}</span>
            </td>
            <td class="p-3.5 font-bold text-emerald-700">${Number(app.gpa).toFixed(2)}</td>
            <td class="p-3.5 text-slate-600 truncate max-w-[160px]">${app.old_school || '-'}</td>
            <td class="p-3.5">
                <span class="px-2.5 py-1 rounded-full text-[11px] font-bold ${badgeClass}">
                    ${app.status}
                </span>
            </td>
            <td class="p-3.5 text-center">
                <div class="flex items-center justify-center gap-1.5">
                    <button onclick="openReviewModal(${app.id})" class="px-2.5 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg text-xs font-semibold flex items-center gap-1">
                        <i data-lucide="eye" class="w-3.5 h-3.5"></i>
                        <span>ตรวจข้อมูล</span>
                    </button>
                    <a href="${printPdfLink}" target="_blank" title="ใบสมัคร PDF" class="p-1.5 text-slate-400 hover:text-blue-600 rounded-lg">
                        <i data-lucide="file-text" class="w-4 h-4"></i>
                    </a>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });

    if (window.lucide) lucide.createIcons();
}

// --------------------------------------------------------------------------
// Admin Modal & Status Management
// --------------------------------------------------------------------------
let activeReviewApplicant = null;

async function openReviewModal(applicantId) {
    const app = allApplicants.find(a => a.id === applicantId);
    if (!app) return;
    activeReviewApplicant = app;

    document.getElementById("modalSubTitle").textContent = `รหัสใบสมัคร APP-${String(app.id).padStart(5, '0')} | ${app.prefix_th}${app.first_name_th} ${app.last_name_th}`;

    const body = document.getElementById("modalBody");
    body.innerHTML = `
        <div class="bg-slate-50 p-4 rounded-xl border border-slate-200 grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div><span class="text-slate-400">เลข ปชช.:</span> <strong class="font-mono block">${app.citizen_id}</strong></div>
            <div><span class="text-slate-400">ระดับ/สาขา:</span> <strong class="block">${app.education_level} ${app.first_choice_major}</strong></div>
            <div><span class="text-slate-400">เกรดเฉลี่ย GPA:</span> <strong class="block text-emerald-600">${Number(app.gpa).toFixed(2)}</strong></div>
            <div><span class="text-slate-400">เบอร์โทร:</span> <strong class="font-mono block">${app.phone}</strong></div>
            <div class="col-span-2"><span class="text-slate-400">โรงเรียนเดิม:</span> <strong class="block">${app.old_school} (${app.old_school_province})</strong></div>
            <div class="col-span-2"><span class="text-slate-400">ผู้ปกครอง:</span> <strong class="block">${app.guardian_name || '-'} (${app.guardian_relation || ''} โทร: ${app.guardian_phone || '-'})</strong></div>
        </div>

        <div>
            <h4 class="font-bold text-slate-800 mb-2">เอกสารหลักฐานที่แนบ:</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="modalDocsList">
                ${(app.documents || []).map(doc => `
                    <div class="p-3 border border-slate-200 rounded-xl bg-white flex justify-between items-center">
                        <div>
                            <span class="font-bold text-slate-700 block">${doc.doc_type}</span>
                            <span class="text-[11px] text-slate-400 font-mono">${doc.filename}</span>
                        </div>
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${doc.status === 'ถูกต้อง' ? 'bg-emerald-100 text-emerald-800' : (doc.status === 'ต้องแก้ไข' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800')}">${doc.status}</span>
                    </div>
                `).join('')}
            </div>
        </div>

        <div>
            <label class="block font-bold text-slate-700 mb-1">ข้อความหมายเหตุ / แจ้งเตือนผู้สมัคร:</label>
            <textarea id="modalAdminNote" rows="2" class="w-full p-2.5 rounded-xl border border-slate-300 text-xs">${app.admin_notes || ''}</textarea>
        </div>

        <div class="pt-4 border-t border-slate-200 flex flex-wrap justify-between items-center gap-3">
            <div class="flex items-center gap-2">
                <span class="text-slate-500">สถานะปัจจุบัน:</span>
                <span class="font-bold text-blue-700">${app.status}</span>
            </div>
            <div class="flex flex-wrap gap-2">
                <button onclick="updateApplicantStatus('เอกสารไม่สมบูรณ์')" class="px-3.5 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow-sm">
                    แจ้งเอกสารไม่สมบูรณ์
                </button>
                <button onclick="updateApplicantStatus('ผ่านการคัดเลือก')" class="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-sm">
                    อนุมัติผ่านการคัดเลือก
                </button>
                <button onclick="enrollApplicantModal(${app.id})" class="px-3.5 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold shadow-sm">
                    มอบตัว & ออกรหัสนักศึกษา
                </button>
            </div>
        </div>
    `;

    document.getElementById("reviewModal").classList.remove("hidden");
    if (window.lucide) lucide.createIcons();
}

function closeReviewModal() {
    document.getElementById("reviewModal").classList.add("hidden");
}

async function updateApplicantStatus(newStatus) {
    if (!activeReviewApplicant) return;
    const notes = document.getElementById("modalAdminNote").value;

    if (!isStaticMode) {
        try {
            const resp = await fetch(`/api/admin/applicants/${activeReviewApplicant.id}/status`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ status: newStatus, admin_notes: notes })
            });
            if (resp.ok) {
                alert(`เปลี่ยนสถานะเป็น "${newStatus}" เรียบร้อยแล้ว`);
                closeReviewModal();
                loadAdminDashboard();
                return;
            }
        } catch(e) {
            isStaticMode = true;
        }
    }

    // Static mode
    let list = getLocalData();
    let app = list.find(a => a.id === activeReviewApplicant.id);
    if (app) {
        app.status = newStatus;
        app.admin_notes = notes;
        saveLocalData(list);
    }
    alert(`เปลี่ยนสถานะเป็น "${newStatus}" เรียบร้อยแล้ว`);
    closeReviewModal();
    loadAdminDashboard();
}

async function enrollApplicantModal(applicantId) {
    if (!confirm("ยืนยันการรับมอบตัว? ระบบจะทำการออกรหัสนักศึกษามาตรฐาน ศธ.02 อัตโนมัติ")) return;

    if (!isStaticMode) {
        try {
            const resp = await fetch(`/api/admin/applicants/${applicantId}/enroll`, { method: "POST" });
            if (resp.ok) {
                const res = await resp.json();
                alert(`มอบตัวสำเร็จ! ออกรหัสนักศึกษาใหม่เรียบร้อย: ${res.student_id}`);
                closeReviewModal();
                loadAdminDashboard();
                return;
            }
        } catch(e) {
            isStaticMode = true;
        }
    }

    // Static mode student ID generator
    let list = getLocalData();
    let app = list.find(a => a.id === applicantId);
    if (app) {
        const levelCode = app.education_level === "ปวช." ? "2" : "3";
        const majorCode = resolveMajorCodeClient(app.education_level, app.first_choice_major);
        const majorSuffix = majorCode.slice(-4);
        const seq = String(list.filter(a => a.student_id).length + 1).padStart(4, "0");
        const studentId = `68${levelCode}${majorSuffix}${seq}`;

        app.status = "มอบตัวแล้ว";
        app.student_id = studentId;
        app.admin_notes = "มอบตัวเสร็จสิ้น ออกรหัสนักศึกษาเรียบร้อย";
        saveLocalData(list);
        alert(`มอบตัวสำเร็จ! ออกรหัสนักศึกษาใหม่: ${studentId}`);
        closeReviewModal();
        loadAdminDashboard();
    }
}

function resolveMajorCodeClient(level, majorName) {
    const isPvs = (level || "").includes("ปวส");
    const prefix = isPvs ? "3" : "2";
    const name = (majorName || "");

    if (name.includes("สารสนเทศ")) return `${prefix}0901`;
    if (name.includes("บัญชี")) return `${prefix}0201`;
    if (name.includes("ธุรกิจดิจิทัล") || name.includes("คอมพิวเตอร์ธุรกิจ")) return `${prefix}0204`;
    if (name.includes("ตลาด")) return `${prefix}0202`;
    if (name.includes("ไฟฟ้า")) return `${prefix}0104`;
    if (name.includes("อิเล็กทรอนิกส์")) return `${prefix}0105`;
    if (name.includes("เทคนิคคอมพิวเตอร์")) return "20128";
    if (name.includes("เทคโนโลยีคอมพิวเตอร์")) return "30128";
    if (name.includes("คอมพิวเตอร์")) return `${prefix}0128`;
    if (name.includes("การผลิต") || name.includes("ช่างกล")) return `${prefix}0102`;
    if (name.includes("ซ่อมบำรุง")) return `${prefix}0107`;
    if (name.includes("ยานยนต์") || name.includes("ช่างยนต์")) return `${prefix}0101`;
    if (name.includes("เมคคาทรอนิกส์")) return `${prefix}0127`;
    return `${prefix}0101`;
}

// --------------------------------------------------------------------------
// Export Standard ศธ.02 (.xlsx and .csv) - Client & Server Ready
// --------------------------------------------------------------------------
function exportStd02(format) {
    if (!isStaticMode) {
        window.location.href = `/api/admin/export/std02?format=${format}`;
        return;
    }

    // Client-side export using SheetJS for GitHub Pages
    const rows = allApplicants.map((app, idx) => ({
        "ลำดับ": idx + 1,
        "เลขประจำตัวนักศึกษา (ศธ.02)": app.student_id || "-",
        "เลขประจำตัวประชาชน (13 หลัก)": f_quote(app.citizen_id),
        "คำนำหน้า": app.prefix_th,
        "ชื่อ (ภาษาไทย)": app.first_name_th,
        "นามสกุล (ภาษาไทย)": app.last_name_th,
        "เพศ": app.gender,
        "วันเดือนปีเกิด": formatThaiDate(app.birth_date),
        "สัญชาติ": "ไทย",
        "ศาสนา": app.religion || "พุทธ",
        "ระดับการศึกษา": app.education_level,
        "รหัสสาขาวิชา": resolveMajorCodeClient(app.education_level, app.first_choice_major),
        "สาขาวิชา (อันดับ 1)": app.first_choice_major,
        "สาขาวิชา (อันดับ 2)": app.second_choice_major || "-",
        "ประเภทโควตา": app.quota_type || "สอบคัดเลือกทั่วไป",
        "ผลการเรียนเฉลี่ย (GPA)": Number(app.gpa || 3.0).toFixed(2),
        "โรงเรียนเดิม": app.old_school,
        "จังหวัดโรงเรียนเดิม": app.old_school_province,
        "เบอร์โทรศัพท์ผู้สมัคร": app.phone,
        "อีเมล": app.email || "-",
        "บ้านเลขที่": app.address_no,
        "หมู่ที่": app.moo || "-",
        "ตำบล/แขวง": app.subdistrict,
        "อำเภอ/เขต": app.district,
        "จังหวัด": app.province,
        "รหัสไปรษณีย์": app.postal_code,
        "ชื่อ-สกุล บิดา": app.father_name || "-",
        "ชื่อ-สกุล มารดา": app.mother_name || "-",
        "ชื่อ-สกุล ผู้ปกครอง": app.guardian_name || "-",
        "ความสัมพันธ์ผู้ปกครอง": app.guardian_relation || "-",
        "สถานะในระบบรับสมัคร": app.status
    }));

    if (window.XLSX) {
        const worksheet = XLSX.utils.json_to_sheet(rows);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "ศธ.02_ข้อมูลนักเรียน");
        if (format === "csv") {
            XLSX.writeFile(workbook, "std02_vocational_students_2568.csv", { bookType: "csv" });
        } else {
            XLSX.writeFile(workbook, "std02_vocational_students_2568.xlsx");
        }
    } else {
        alert("กำลังดาวน์โหลดข้อมูล...");
    }
}

function f_quote(str) {
    return str ? `'${str}` : "";
}

function formatThaiDate(dateStr) {
    if (!dateStr) return "";
    try {
        const p = dateStr.split("-");
        if (p.length === 3) {
            return `${p[2]}/${p[1]}/${parseInt(p[0]) + 543}`;
        }
    } catch(e) {}
    return dateStr;
}
