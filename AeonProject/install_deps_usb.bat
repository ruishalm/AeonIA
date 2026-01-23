@echo off
title INSTALAR DEPENDENCIAS NO PENDRIVE
color 0B

echo ==================================================
echo   INSTALADOR DE DEPENDENCIAS (MODO PORTATIL)
echo ==================================================

:: 1. Descobre onde estamos
set "AEON_DIR=%~dp0"
pushd "%AEON_DIR%.."
set "USB_ROOT=%CD%"
popd

:: 2. Define caminho do Python Portatil
set "PYTHON_EXE=%USB_ROOT%\Python\python.exe"

if not exist "%PYTHON_EXE%" (
    color 0C
    echo [ERRO] Python portatil nao encontrado em:
    echo "%PYTHON_EXE%"
    echo.
    echo Certifique-se de que extraiu o WinPython e renomeou a pasta
    echo interna ^(que contem python.exe^) para 'Python' na raiz do pendrive.
    pause
    exit /b
)

if not exist "%AEON_DIR%requirements.txt" (
    color 0C
    echo [ERRO] Arquivo requirements.txt nao encontrado em:
    echo "%AEON_DIR%requirements.txt"
    pause
    exit /b
)

echo [INFO] Usando Python em: "%PYTHON_EXE%"

:: Teste de sanidade do Python
"%PYTHON_EXE%" -c "print('Python OK')" >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERRO] O Python nao esta respondendo. Verifique se copiou a pasta inteira do WinPython.
    pause
    exit /b
)

:: 3. Verifica e Instala PIP se necessario
echo [INFO] Verificando PIP (Isso pode demorar no USB)...
"%PYTHON_EXE%" -m pip --version
if %errorlevel% neq 0 (
    echo.
    echo [AVISO] PIP nao encontrado. Tentando ativar via ensurepip...
    "%PYTHON_EXE%" -m ensurepip --default-pip
    if %errorlevel% neq 0 (
        color 0C
        echo [ERRO] Nao foi possivel ativar o PIP.
        echo Se voce baixou o 'Python Embeddable' em vez do WinPython:
        echo 1. Abra a pasta Python no pendrive.
        echo 2. Abra o arquivo pythonXX._pth num editor de texto.
        echo 3. Descomente ^(remova o #^) da linha 'import site'.
        echo 4. Tente rodar este script novamente.
        pause
        exit /b
    )
)

:: 4. Instala as dependencias
echo [INFO] Instalando bibliotecas do requirements.txt...
echo.

"%PYTHON_EXE%" -m pip install --no-warn-script-location -r "%AEON_DIR%requirements.txt"

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERRO] Falha na instalacao. Verifique sua internet e o log acima.
    pause
    exit /b
)

echo.
echo ==================================================
echo      INSTALACAO CONCLUIDA COM SUCESSO!
echo ==================================================
pause