@echo off
REM WordPress Monitor - Quick launcher
REM Usage: monitor.bat [args]
REM Examples:
REM   monitor.bat check --quick
REM   monitor.bat check --fast --pages /
REM   monitor.bat check --fast --limit 10

"%~dp0venv\Scripts\python.exe" "%~dp0cli.py" %*
