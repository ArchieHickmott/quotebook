@echo off
cd /d %~dp0
@REM uncomment to auto-install packages
@REM pip install -r requirements.txt
python -m app  > logs.log
