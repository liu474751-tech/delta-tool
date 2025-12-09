@echo off
chcp 65001 >nul
title Delta Tool - Desktop Client

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py
) else (
    echo Virtual environment not found!
    echo Please run install.bat first.
    pause
)
