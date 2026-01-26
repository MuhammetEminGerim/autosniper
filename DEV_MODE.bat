@echo off
echo === AutoSniper Geliştirme Modu ===
echo.

echo 1. Backend başlatılıyor...
start "AutoSniper Backend" cmd /k "cd backend && python -m uvicorn app.main:app --port 8000"

echo 2. Backend'in başlaması bekleniyor (5 saniye)...
timeout /t 5 /nobreak > nul

echo 3. Electron başlatılıyor...
start "AutoSniper Frontend" cmd /k "cd frontend && npm run dev"

echo 4. Electron Desktop başlatılıyor...
timeout /t 3 /nobreak > nul
npm run electron

echo.
echo Tüm servisler başlatıldı.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
pause
