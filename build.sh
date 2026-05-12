#!/bin/bash
echo ""
echo " ╔══════════════════════════════════════════╗"
echo " ║   Compilador · Lançamentos Fênix         ║"
echo " ╚══════════════════════════════════════════╝"
echo ""

# ── verifica se Python está disponível
if ! command -v python3 &>/dev/null; then
    echo " [ERRO] Python3 não encontrado."
    echo " Execute: sudo apt install python3 python3-pip python3-tk"
    exit 1
fi

# ── verifica versão mínima (3.10)
python3 -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)"
if [ $? -ne 0 ]; then
    echo " [ERRO] Python 3.10 ou superior é necessário."
    echo " Versão instalada: $(python3 --version)"
    echo " Veja: https://python.org/downloads"
    exit 1
fi

# ── verifica tkinter (no Linux vem separado)
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo " [AVISO] tkinter não encontrado. Instalando..."
    sudo apt install python3-tk -y
fi

echo " [1/4] Atualizando pip..."
python3 -m pip install --upgrade pip --quiet

echo " [2/4] Instalando dependências..."
python3 -m pip install PyMuPDF pandas openpyxl pyinstaller --quiet

echo " [3/4] Compilando executável..."
python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name "LancamentosFenix" \
    --hidden-import=fitz \
    --hidden-import=pandas \
    --hidden-import=openpyxl \
    --hidden-import=difflib \
    main.py

echo ""
if [ -f "dist/LancamentosFenix" ]; then
    chmod +x dist/LancamentosFenix
    echo " [4/4] Concluído com sucesso!"
    echo ""
    echo " Executável gerado em:"
    echo " $(pwd)/dist/LancamentosFenix"
    echo ""
else
    echo " [ERRO] A compilação falhou. Verifique as mensagens acima."
    exit 1
fi
