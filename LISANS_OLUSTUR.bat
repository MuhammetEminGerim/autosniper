@echo off
echo === AutoSniper Lisans Generator ===
echo.

python license_generator.py

if errorlevel 1 (
    echo.
    echo Hata: Python kurulu değil veya script'te sorun var!
    echo.
    echo Cozumler:
    echo 1. Python 3.7+ kurun
    echo 2. Script'in dogru klasorde oldugundan emin olun
    echo 3. Backend klasorunun var oldugunu kontrol edin
    echo.
    pause
    exit /b 1
)

echo.
echo Lisans olusturma tamamlandi!
pause
