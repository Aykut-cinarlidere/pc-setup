@echo off
title PC Setup - EXE Builder
echo.
echo  ========================
echo   PC Setup - EXE Builder
echo  ========================
echo.

:: Python'u bul (PATH'de olmasa bile)
set PYTHON=
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
) do (
    if exist %%p (
        set PYTHON=%%p
        goto :found
    )
)

:: PATH'de ara
python --version >nul 2>nul
if %errorlevel% == 0 (
    set PYTHON=python
    goto :found
)

:: Python yok, indir ve kur
echo  [!] Python bulunamadi. Indiriliyor...
curl -L -o "%TEMP%\python-installer.exe" "https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe"
echo  [*] Python kuruluyor...
"%TEMP%\python-installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1
set PYTHON="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
echo  [+] Python kuruldu.
echo.

:found
echo  [+] Python bulundu: %PYTHON%
echo.

:: pip ile pyinstaller kur
echo  [*] PyInstaller yukleniyor...
%PYTHON% -m pip install pyinstaller --quiet --disable-pip-version-check
echo  [+] PyInstaller hazir.
echo.

:: EXE olustur
echo  [*] EXE olusturuluyor...
%PYTHON% -m PyInstaller --onefile --windowed --name "PC-Setup" main.py

echo.
echo  ========================
echo  [+] EXE olusturuldu: dist\PC-Setup.exe
echo  ========================
echo.
pause
