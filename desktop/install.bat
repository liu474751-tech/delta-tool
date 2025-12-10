@echo off
chcp 65001 >nul
title Delta Tool - Desktop Client Setup

echo ========================================
echo   Delta Tool Desktop Client Installer
echo ========================================
echo.

:: Check Python with multiple methods
set PYTHON_CMD=

:: Try python command
python --version >nul 2>&1
if not errorlevel 1 (
    :: Verify it's real Python, not Windows Store stub
    python -c "import sys; sys.exit(0)" >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=python
        goto :python_found
    )
)

:: Try py launcher
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    goto :python_found
)

:: Try common install paths
if exist "C:\Python312\python.exe" (
    set PYTHON_CMD=C:\Python312\python.exe
    goto :python_found
)
if exist "C:\Python311\python.exe" (
    set PYTHON_CMD=C:\Python311\python.exe
    goto :python_found
)
if exist "C:\Python310\python.exe" (
    set PYTHON_CMD=C:\Python310\python.exe
    goto :python_found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    goto :python_found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    goto :python_found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
    goto :python_found
)

:: Python not found
echo [ERROR] Python not found!
echo.
echo Please install Python 3.10 or higher:
echo.
echo   Option 1: Download from official website
echo   https://www.python.org/downloads/
echo.
echo   IMPORTANT: During installation, check the box:
echo   [x] "Add Python to PATH"
echo.
echo   Option 2: Install via Windows Store
echo   Search "Python 3.12" in Microsoft Store
echo.
echo After installing Python, run this script again.
echo.
pause
exit /b 1

:python_found
echo [OK] Python found: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

:: Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)
echo [OK] Virtual environment ready
echo.

:: Check if venv was created successfully
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment creation failed
    echo Please ensure Python is properly installed
    pause
    exit /b 1
)

:: Activate and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat

echo Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip -q

echo Installing core packages...
venv\Scripts\pip.exe install PyQt6 mss Pillow pywin32 psutil keyboard -q
if errorlevel 1 (
    echo [WARNING] Some packages may have failed to install
)

echo Installing data packages...
venv\Scripts\pip.exe install numpy pandas requests -q

echo.
echo [OK] Core dependencies installed
echo.
echo ========================================
echo   Select OCR Engine
echo ========================================
echo.
echo   1. EasyOCR (Recommended - Easy to install, ~500MB)
echo   2. PaddleOCR (Best Chinese OCR, ~1.5GB download)
echo   3. Skip OCR (Can add later)
echo.
set /p ocr_choice="Enter choice [1/2/3]: "

if "%ocr_choice%"=="1" (
    echo.
    echo Installing EasyOCR (this may take a few minutes)...
    venv\Scripts\pip.exe install easyocr
    if errorlevel 1 (
        echo [WARNING] EasyOCR installation had issues
    ) else (
        echo [OK] EasyOCR installed successfully
    )
) else if "%ocr_choice%"=="2" (
    echo.
    echo Installing PaddleOCR (this may take 10+ minutes)...
    venv\Scripts\pip.exe install paddlepaddle
    venv\Scripts\pip.exe install paddleocr
    if errorlevel 1 (
        echo [WARNING] PaddleOCR installation had issues
    ) else (
        echo [OK] PaddleOCR installed successfully
    )
) else (
    echo.
    echo Skipping OCR installation
    echo You can install later with:
    echo   venv\Scripts\pip.exe install easyocr
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To start the application:
echo   Double-click "run.bat"
echo.
echo Hotkeys:
echo   F9  - Capture screen
echo   F10 - Toggle monitoring
echo   F11 - Recognize screen
echo.
pause
