import fitz  # PyMuPDF
import pandas as pd
import re
import datetime

def extrair_extrato_de_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()

    linhas = text.splitlines()
    registros = []
    cliente_atual = None
    data_ultimo_cred = None
    i = 0

    while i < len(linhas):
        linha = linhas[i].strip()

        cliente_match = re.match(r"^(\d+)\s+-\s+(.+)$", linha)
        if cliente_match:
            cliente_nome = cliente_match.group(2).strip()
            cliente_atual = cliente_nome
            i += 1
            continue

        entrada_match = re.match(r"^(\d{4,5}) (.+?)\s*$", linha)
        if entrada_match and cliente_atual:
            descricao_completa = entrada_match.group(2).strip()
            try:
                data_geracao = linhas[i + 1].strip()
                data_venc = linhas[i + 2].strip()
                data_liq = linhas[i + 3].strip()
                data_cred = linhas[i + 4].strip()
                valor = linhas[i + 5].strip().replace("R$ ", "").replace(".", "").replace(",", ".")

                if re.match(r"^-?\d+\.\d{2}$", valor):
                    data_ultimo_cred = data_cred
                    registros.append({
                        "Data": data_cred,
                        "Descrição": f"{cliente_atual} - {descricao_completa}",
                        "Valor": float(valor)
                    })
                    i += 6
                    continue
            except IndexError:
                pass

        total_match = re.match(r"^R\$\s*([\d\.]+,\d{2})$", linha)
        if total_match and cliente_atual:
            valor_total = total_match.group(1).replace(".", "").replace(",", ".")
            registros.append({
                "Data": data_ultimo_cred,
                "Descrição": f"{cliente_atual} - pagamento",
                "Valor": float(valor_total)
            })

        i += 1

    df = pd.DataFrame(registros)
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors='coerce')
    return df

# Exemplo de uso:
df = extrair_extrato_de_pdf("caminho arquivo de conversão.pdf")
df.to_excel("extrato_formatado.xlsx", index=False)
print('Extração concluída com sucesso!')
