@echo off
cd /d %~dp0
<<<<<<< HEAD
pip install -r requirements.txt
python -m app %*
=======
@REM uncomment to auto-install packages
@REM pip install -r requirements.txt
echo HI
python -m quotebook --host 0.0.0.0 --port 5000
>>>>>>> main
