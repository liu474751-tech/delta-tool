@echo off
chcp 65001 >nul
title 三角洲工具 - Streamlit服务

:loop
echo [%TIME%] 启动 Streamlit...
"%~dp0venv\Scripts\streamlit.exe" run app.py
echo [%TIME%] Streamlit 已停止，3秒后重启...
timeout /t 3 /nobreak >nul
goto loop
