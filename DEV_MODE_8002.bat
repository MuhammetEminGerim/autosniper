@echo off
echo === AutoSniper Geliştirme Modu (Port 8002) ===
echo.

echo 1. Backend başlatılıyor (Port 8002)...
start "AutoSniper Backend" cmd /k "cd backend && python -m uvicorn app.main:app --port 8002"

echo 2. Backend'in başlaması bekleniyor (5 saniye)...
timeout /t 5 /nobreak > nul

echo 3. Electron başlatılıyor (Port 8002)...
start "AutoSniper Frontend" cmd /k "cd frontend && npm run dev"

echo 4. Electron Desktop başlatılıyor...
timeout /t 3 /nobreak > nul
set BACKEND_URL=http://localhost:8002 && npm run electron

echo.
echo Tüm servisler başlatıldı.
echo Backend: http://localhost:8002
echo Frontend: http://localhost:3000
pause
