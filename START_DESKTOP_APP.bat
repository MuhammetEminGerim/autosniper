@echo off
echo ================================
echo AutoSniper Desktop App - Baslatici
echo ================================
echo.

echo [1/3] Docker baslatiyor...
docker-compose up -d
timeout /t 3 /nobreak >nul

echo.
echo [2/3] Frontend dev server baslatiyor...
start cmd /k "cd frontend && npm run dev"
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Electron baslatiyor...
timeout /t 3 /nobreak >nul
npm run electron

echo.
echo Uygulama kapatildi.
pause
