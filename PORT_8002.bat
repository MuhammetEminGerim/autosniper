@echo off
echo === AutoSniper Port 8002 Değiştirme ===
echo.

echo 1. Backend port'u 8002'ye değiştiriliyor...
powershell -Command "(Get-Content electron\main.js) -replace 'const BACKEND_PORT = 8001;', 'const BACKEND_PORT = 8002;' | Set-Content electron\main.js"

echo 2. Frontend URL'i güncelleniyor...
powershell -Command "(Get-Content electron\main.js) -replace 'http://localhost:8001', 'http://localhost:8002' | Set-Content electron\main.js"

echo 3. Program yeniden build ediliyor...
npm run build

echo.
echo Port 8002'ye değiştirildi ve build tamamlandı!
echo Yeni setup dosyası: dist\AutoSniper Setup 1.0.0.exe
echo.
echo Test etmek için:
echo cd dist\win-unpacked
echo AutoSniper.exe
pause
