import pandas as pd
import re
from difflib import get_close_matches

def gerar_lancamentos_contabeis_fuzzy(extrato_path, plano_contas_path, saida_path):
    df_extrato = pd.read_excel(extrato_path, parse_dates=["Data"])
    df_plano = pd.read_excel(plano_contas_path)
    df_plano["Nome"] = df_plano["Nome"].str.strip().str.lower()

    mapa_clientes = {
        nome: codigo for codigo, nome in zip(df_plano["Código"], df_plano["Nome"])
    }
    nomes_clientes = list(mapa_clientes.keys())

    lancamentos = []

    for _, row in df_extrato.iterrows():
        descricao = str(row["Descrição"])
        data = row["Data"]
        valor = round(abs(row["Valor"]), 2)

        cliente_match = re.match(r"^(.*?)\s*-", descricao)
        nome_extraido = cliente_match.group(1).strip().lower() if cliente_match else ""

        nome_proximo = get_close_matches(nome_extraido, nomes_clientes, n=1, cutoff=1)
        conta_cliente = mapa_clientes.get(nome_proximo[0]) if nome_proximo else None

        if "aluguel" in descricao.lower():
            continue
        elif "bônus" in descricao.lower():
            lancamentos.append({
                "Data": data, "Débito": 1155,
                "Crédito": conta_cliente or 3930, "Valor": valor,
                "Descrição": descricao
            })
        elif "taxa bancária" in descricao.lower():
            lancamentos.append({
                "Data": data, "Débito": 1155,
                "Crédito": conta_cliente or 3930, "Valor": valor,
                "Descrição": descricao
            })
        elif "pagamento a maior" in descricao.lower():
            lancamentos.append({
                "Data": data, "Débito": conta_cliente or 3930,
                "Crédito": 2836, "Valor": valor,
                "Descrição": descricao
            })
        elif "juros" in descricao.lower():
            lancamentos.append({
                "Data": data, "Débito": conta_cliente or 3930,
                "Crédito": 2836, "Valor": valor,
                "Descrição": descricao
            })
        elif "multa" in descricao.lower():
            lancamentos.append({
                "Data": data, "Débito": conta_cliente or 3930,
                "Crédito": 4499, "Valor": valor,
                "Descrição": descricao
            })
        elif "pagamento" in descricao.lower():
            if conta_cliente:
                lancamentos.append({
                    "Data": data, "Débito": 51,
                    "Crédito": conta_cliente, "Valor": valor,
                    "Descrição": descricao
                })
            else:
                lancamentos.append({
                    "Data": data, "Débito": 51,
                    "Crédito": 3930, "Valor": valor,
                    "Descrição": descricao
                })

    df_lcto = pd.DataFrame(lancamentos)
    df_lcto["Data"] = pd.to_datetime(df_lcto["Data"])

    df_lcto.insert(0, "Sequência", 0)
    df_lcto["Histórico"] = 547

    colunas_finais = ["Sequência", "Data", "Débito", "Crédito", "Valor", "Histórico", "Descrição"]
    df_lcto = df_lcto[colunas_finais]

    df_lcto.to_excel(saida_path, index=False)
    return saida_path

# Exemplo de uso:
gerar_lancamentos_contabeis_fuzzy("extrato_formatado.xlsx", "arquivo_plano_de_contas.xlsx", "lancamentos_gerados.xlsx")
print('Lançamentos gerados com sucesso!')
