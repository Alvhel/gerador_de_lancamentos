@echo off
chcp 65001 >nul
title Compilador · Lançamentos Contábeis Fênix

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   Compilador · Lançamentos Fênix         ║
echo  ╚══════════════════════════════════════════╝
echo.

REM ── verifica se Python está disponível
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERRO] Python não encontrado no PATH.
    echo  Instale o Python em https://python.org e marque "Add to PATH".
    pause
    exit /b 1
)

echo  [1/4] Atualizando pip...
python -m pip install --upgrade pip --quiet

echo  [2/4] Instalando dependências...
python -m pip install PyMuPDF pandas openpyxl pyinstaller --quiet

echo  [3/4] Compilando executável...
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "LancamentosFenix" ^
    --hidden-import=fitz ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=difflib ^
    main.py

echo.
if exist "dist\LancamentosFenix.exe" (
    echo  [4/4] Concluído com sucesso!
    echo.
    echo  Executável gerado em:
    echo  %cd%\dist\LancamentosFenix.exe
    echo.
    explorer dist
) else (
    echo  [ERRO] A compilação falhou. Verifique as mensagens acima.
)

pause
