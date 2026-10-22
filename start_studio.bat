@echo off
title ReelCraft AI Studio
cd /d "%~dp0"
echo ====================================================================
echo            REELCRAFT AI - FACELESS REELS AUTO-STUDIO
echo ====================================================================
echo.
echo Starting local server...
start "" "http://localhost:8000"
python run.py
pause
