@echo off
setlocal

set "AGENT_DIR=%~dp0"
set "PYTHON_DIR=%AGENT_DIR%python"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "SCRIPT=%AGENT_DIR%send_once_monitor.py"
set "ANIMATION_INSTALL=%AGENT_DIR%animation_install.ps1"
set "ANIMATION_CAR=%AGENT_DIR%animation_car.ps1"

:: === ��������: ���� Python ��� ���������� ===
if exist "%PYTHON_EXE%" (
    echo [INFO] Python ������. ������ ����������� � ���������...
    goto :run_monitoring
)

:: === ��������� Python ===
echo [INFO] ��������� Python (embed) � ������������...

:: ���������� �������� ��������� � ������� ����
powershell -NoProfile -ExecutionPolicy Bypass -File "%ANIMATION_INSTALL%"

:: ������ �����
mkdir "%PYTHON_DIR%" 2>nul

:: ��������� � ������������� Python
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.6/python-3.12.6-embed-amd64.zip' -OutFile '%PYTHON_DIR%\python.zip'"
powershell -Command "Expand-Archive -Path '%PYTHON_DIR%\python.zip' -DestinationPath '%PYTHON_DIR%' -Force"
del "%PYTHON_DIR%\python.zip"

:: �������� site-packages
copy "%PYTHON_DIR%\python312._pth" "%PYTHON_DIR%\python312._pth.bak" >nul
powershell -Command "(Get-Content '%PYTHON_DIR%\python312._pth') -replace '#import site','import site' | Set-Content '%PYTHON_DIR%\python312._pth'"

:: ������������� pip � ������
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%AGENT_DIR%get-pip.py'"
"%PYTHON_EXE%" "%AGENT_DIR%get-pip.py" --no-warn-script-location
del "%AGENT_DIR%get-pip.py"
"%PYTHON_EXE%" -m pip install requests psutil speedtest-cli --quiet

:run_monitoring
:: === ������ ����������� � ��������� ������ ===
start "����������..." /B powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.Interaction]::AppActivate('����������...'); & '%ANIMATION_CAR%'"

:: ��������� Python-������ � �Ĩ� ��� ����������
"%PYTHON_EXE%" "%SCRIPT%"

:: ����� ���������� � ��������� �������� � �������
taskkill /fi "WindowTitle eq CarAnim*" /f >nul 2>&1
exit