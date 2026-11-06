@echo off
chcp 65001 > nul
title เชื่อมต่อและอัปโหลดขึ้น GitHub (Push to GitHub)
echo =========================================================================
echo   เชื่อมต่อและเปิดเว็บรับสมัครเรียนออนไลน์บน GitHub Pages
echo =========================================================================
echo.
echo ขั้นตอน:
echo 1. เข้าเว็บ https://github.com/new แล้วสร้าง Repository ใหม่ (แนะนำตั้งเป็น Public)
echo 2. คัดลอก URL ของ Repository มาวางในช่องด้านล่างนี้
echo.
set /p REPO_URL="กรุณาวาง URL ของ GitHub Repository (เช่น https://github.com/username/repo.git): "

if "%REPO_URL%"=="" (
    echo ไม่ได้ระบุ URL ยกเลิกการทำงาน
    pause
    exit /b
)

echo.
echo กำลังเชื่อมต่อ Remote และ Push ขึ้น GitHub (branch: main)...
"C:\Users\TL\.gemini\antigravity\scratch\git\cmd\git.exe" remote remove origin 2>nul
"C:\Users\TL\.gemini\antigravity\scratch\git\cmd\git.exe" remote add origin %REPO_URL%
"C:\Users\TL\.gemini\antigravity\scratch\git\cmd\git.exe" branch -M main
"C:\Users\TL\.gemini\antigravity\scratch\git\cmd\git.exe" push -u origin main

echo.
echo =========================================================================
echo   Push ขึ้น GitHub สำเร็จแล้ว!
echo =========================================================================
echo ขั้นตอนเปิดใช้งานหน้าเว็บ GitHub Pages:
echo 1. ไปที่หน้า GitHub Repository ของคุณ
echo 2. คลิกแท็บ "Settings" (ด้านบน)
echo 3. คลิกเมนู "Pages" (แถบซ้ายมือ)
echo 4. ที่หัวข้อ "Branch" ให้เลือก "main" และโฟลเดอร์ "/ (root)" แล้วกด "Save"
echo 5. รอประมาณ 1-2 นาที คุณจะได้ลิงก์เว็บไซต์ใช้งานได้ฟรีทันที!
echo =========================================================================
pause
