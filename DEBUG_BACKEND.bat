@echo off
echo === AutoSniper Debug Mode ===
echo.

echo 1. Backend'i test ediliyor...
cd dist\win-unpacked\resources\backend
echo Backend dosyası: %CD%\autosniper-backend.exe
echo.

echo Backend çalıştırılıyor...
autosniper-backend.exe

echo.
echo Backend test tamamlandı.
pause
