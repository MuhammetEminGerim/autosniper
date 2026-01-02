@echo off
REM Build script for backend executable (Windows)
REM Packages FastAPI backend with PyInstaller

echo === AutoSniper Backend Build ===
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build backend
echo Building backend executable...
pyinstaller backend.spec

REM Check if build succeeded
if exist "dist\autosniper-backend" (
    echo.
    echo ✅ Build successful!
    echo Output: dist\autosniper-backend\
    echo.
    dir dist\autosniper-backend
) else (
    echo.
    echo ❌ Build failed!
    exit /b 1
)
