@echo off
chcp 65001 > nul
title นำระบบรับสมัครเรียนขึ้น GitHub (Push to GitHub)
echo =========================================================================
echo   กำลังนำโค้ดขึ้น GitHub Repository:
echo   https://github.com/teepanunnmahiran-sys/online-admission-system.git
echo =========================================================================
echo.
echo * หมายเหตุ: หากมีหน้าต่าง Git เด้งขึ้นมาถามการเข้าสู่ระบบ
echo   ให้คลิกปุ่ม "Sign in with your browser" แล้วกดยืนยัน Authorize ในเบราว์เซอร์
echo.
"C:\Users\TL\.gemini\antigravity\scratch\git\cmd\git.exe" remote remove origin 2>nul
"C:\Users\TL\.gemini\antigravity\scratch\git\cmd\git.exe" remote add origin https://github.com/teepanunnmahiran-sys/online-admission-system.git
"C:\Users\TL\.gemini\antigravity\scratch\git\cmd\git.exe" branch -M main
"C:\Users\TL\.gemini\antigravity\scratch\git\cmd\git.exe" push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =========================================================================
    echo   [สำเร็จ] นำโค้ดขึ้น GitHub เรียบร้อยแล้ว!
    echo =========================================================================
    echo.
    echo ขั้นตอนสุดท้ายเพื่อเปิดเว็บ GitHub Pages:
    echo 1. เปิดเว็บ: https://github.com/teepanunnmahiran-sys/online-admission-system/settings/pages
    echo 2. ที่หัวข้อ "Branch" ให้เลือก "main" และเลือก "/ (root)"
    echo 3. กดปุ่ม "Save"
    echo 4. รอประมาณ 1 นาที เว็บจะเปิดให้ทุกคนใช้งานได้ฟรีที่:
    echo    https://teepanunnmahiran-sys.github.io/online-admission-system/
    echo =========================================================================
) else (
    echo.
    echo =========================================================================
    echo   หากยังไม่สำเร็จ กรุณาลองเปิด PowerShell แล้วรันคำสั่ง:
    echo   cd C:\Users\TL\.gemini\antigravity\scratch\online_admission_system
    echo   git push -u origin main
    echo =========================================================================
)
echo.
pause
