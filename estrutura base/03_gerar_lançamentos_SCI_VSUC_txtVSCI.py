import pandas as pd

xlsx_path = "lancamentos_gerados.xlsx"

df = pd.read_excel(xlsx_path)

# Formata a coluna 'Data' para o padrão DD/MM/YYYY
if 'Data' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Data']):
    df['Data'] = df['Data'].dt.strftime("%d/%m/%Y")

df.to_csv("lancamentos_contabeis_layout_sistema.txt", sep=",", index=False)

print("Arquivo TXT gerado com sucesso no layout do sistema.")
