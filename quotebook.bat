@echo off
cd /d %~dp0
@REM pip install -r requirements.txt @REM uncomment to auto-install packages
python -m app %*