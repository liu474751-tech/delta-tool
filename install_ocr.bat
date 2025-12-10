@echo off
chcp 65001 >nul
echo ========================================
echo   Delta Tool - OCR引擎安装工具
echo ========================================
echo.

echo 请选择要安装的OCR引擎:
echo.
echo [1] EasyOCR (推荐，简单易用)
echo [2] PaddleOCR (中文识别更强)
echo [3] 两个都安装
echo [0] 取消
echo.

set /p choice=请输入选项 (0-3): 

if "%choice%"=="1" goto install_easy
if "%choice%"=="2" goto install_paddle
if "%choice%"=="3" goto install_both
if "%choice%"=="0" goto end
goto invalid

:install_easy
echo.
echo 正在安装 EasyOCR...
pip install easyocr
echo.
echo ✅ EasyOCR 安装完成!
pause
goto end

:install_paddle
echo.
echo 正在安装 PaddleOCR...
pip install paddlepaddle paddleocr
echo.
echo ✅ PaddleOCR 安装完成!
pause
goto end

:install_both
echo.
echo 正在安装 EasyOCR 和 PaddleOCR...
pip install easyocr
pip install paddlepaddle paddleocr
echo.
echo ✅ 两个OCR引擎都已安装!
pause
goto end

:invalid
echo.
echo ❌ 无效的选项!
pause
goto end

:end
echo.
echo 按任意键退出...
pause >nul
