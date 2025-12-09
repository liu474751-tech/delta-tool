@echo off
chcp 65001 >nul
title Delta Tool - Desktop Client Setup

echo ========================================
echo   Delta Tool Desktop Client Installer
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

:: Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)
echo [OK] Virtual environment ready
echo.

:: Activate and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat

pip install --upgrade pip -q
pip install PyQt6 mss Pillow pywin32 psutil numpy pandas requests keyboard -q

echo.
echo [CHOICE] Select OCR Engine:
echo   1. EasyOCR (Recommended, easy to install)
echo   2. PaddleOCR (Best for Chinese, larger download)
echo   3. Skip OCR installation
echo.
set /p ocr_choice="Enter choice (1/2/3): "

if "%ocr_choice%"=="1" (
    echo Installing EasyOCR...
    pip install easyocr -q
    echo [OK] EasyOCR installed
) else if "%ocr_choice%"=="2" (
    echo Installing PaddleOCR (this may take a while)...
    pip install paddlepaddle paddleocr -q
    echo [OK] PaddleOCR installed
) else (
    echo Skipping OCR installation
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To run the application:
echo   1. Double-click "run.bat"
echo   2. Or run: venv\Scripts\python.exe main.py
echo.
pause
