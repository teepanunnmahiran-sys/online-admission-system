@echo off
chcp 65001 > nul
title ระบบรับสมัครเรียนออนไลน์ครบวงจร (Online Admission System)
echo =========================================================================
echo   ระบบรับสมัครเรียนออนไลน์ครบวงจร (Online Admission System)
echo   รองรับ Data Validation 13 หลัก, พิมพ์ PDF ใบสมัคร/ใบมอบตัว, และ Export ศธ.02
echo =========================================================================
echo.
echo กำลังเริ่มต้น Web Server ที่: http://127.0.0.1:8000
echo กรุณาเปิดเว็บบราวเซอร์ (Chrome / Edge) แล้วพิมพ์: http://127.0.0.1:8000
echo.
"C:\Users\TL\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause
