@echo off
echo === AutoSniper Debug Mode ===
echo.

echo 1. Electron uygulaması debug modda başlatılıyor...
cd dist\win-unpacked
echo Uygulama yolu: %CD%\AutoSniper.exe
echo.

echo Console modunda başlatılıyor (hata mesajları görünecek)
AutoSniper.exe --enable-logging --v=1

echo.
echo Uygulama kapandı. Hata varsa yukarıda görünür.
pause
