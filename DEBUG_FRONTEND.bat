@echo off
echo === AutoSniper Frontend Test ===
echo.

echo 1. Frontend klasörü kontrol ediliyor...
if not exist "frontend\dist" (
    echo HATA: frontend\dist klasörü bulunamadı!
    echo.
    echo Cozum:
    echo cd frontend
    echo npm run build
    echo.
    pause
    exit /b 1
)

echo 2. Frontend build dosyaları kontrol ediliyor...
if not exist "frontend\dist\index.html" (
    echo HATA: frontend\dist\index.html bulunamadı!
    echo Frontend build edilmemiş olabilir.
    echo.
    echo Cozum:
    echo cd frontend
    echo npm run build
    echo.
    pause
    exit /b 1
)

echo 3. Frontend dosyaları listeleniyor...
dir frontend\dist

echo.
echo Frontend kontrol tamamlandı.
pause
