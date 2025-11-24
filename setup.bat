@echo off
title Graduate Diary v8.0 - Setup
python --version || (
    echo Python not found! Please install Python 3.10+ (3.14 recommended).
    pause
    exit /b
)
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Installation complete.
echo Run: python main.py
pause
