@echo off
echo PC Setup - EXE Builder
echo ========================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python bulunamadi! python.org/downloads adresinden yukleyin.
    pause
    exit /b 1
)

pip install pyinstaller --quiet
echo PyInstaller hazir.

pyinstaller --onefile --windowed --name "PC-Setup" main.py

echo.
echo ========================
echo EXE olusturuldu: dist\PC-Setup.exe
echo ========================
pause
