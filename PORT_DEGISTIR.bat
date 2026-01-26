@echo off
echo === AutoSniper Port Değiştirme ===
echo.

echo 1. Backend port'u 8001'e değiştiriliyor...
powershell -Command "(Get-Content electron\main.js) -replace 'const BACKEND_PORT = 8000;', 'const BACKEND_PORT = 8001;' | Set-Content electron\main.js"

echo 2. Frontend URL'i güncelleniyor...
powershell -Command "(Get-Content electron\main.js) -replace 'http://localhost:8000', 'http://localhost:8001' | Set-Content electron\main.js"

echo 3. Program yeniden build ediliyor...
npm run build

echo.
echo Port değiştirildi ve build tamamlandı!
echo Yeni setup dosyası: dist\AutoSniper Setup 1.0.0.exe
pause
