@echo off
chcp 65001 >nul
title 三角洲工具 - 启动器
color 0A

echo.
echo ╔══════════════════════════════════════════════╗
echo ║     🎮 三角洲战术终端 - 快速启动器         ║
echo ╚══════════════════════════════════════════════╝
echo.

:menu
echo 请选择要启动的模块:
echo.
echo [1] 🖥️  桌面客户端 (实时记录)
echo [2] 🌐 Web分析页面 (数据分析)
echo [3] 📊 同时启动两个模块
echo [4] ❌ 退出
echo.

set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" goto desktop
if "%choice%"=="2" goto web
if "%choice%"=="3" goto both
if "%choice%"=="4" goto end
echo 无效选项，请重新选择
goto menu

:desktop
echo.
echo 🚀 正在启动桌面客户端...
echo.
cd desktop
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python main.py
) else (
    echo ⚠️ 虚拟环境不存在，使用系统Python
    python main.py
)
goto end

:web
echo.
echo 🚀 正在启动Web分析页面...
echo.
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    streamlit run app.py
) else (
    echo ⚠️ 虚拟环境不存在，使用系统Python
    streamlit run app.py
)
goto end

:both
echo.
echo 🚀 正在同时启动两个模块...
echo.
echo 正在启动桌面客户端...
cd desktop
if exist venv\Scripts\activate.bat (
    start "桌面客户端" cmd /k "call venv\Scripts\activate.bat && python main.py"
) else (
    start "桌面客户端" cmd /k "python main.py"
)

cd ..
timeout /t 2 /nobreak >nul

echo 正在启动Web分析页面...
if exist venv\Scripts\activate.bat (
    start "Web分析页面" cmd /k "call venv\Scripts\activate.bat && streamlit run app.py"
) else (
    start "Web分析页面" cmd /k "streamlit run app.py"
)

echo.
echo ✅ 两个模块已在新窗口中启动！
echo.
pause
goto end

:end
echo.
echo 👋 感谢使用三角洲战术终端！
echo.
timeout /t 2 /nobreak >nul
exit
