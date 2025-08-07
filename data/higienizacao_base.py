import pandas as pd

# Caminho do arquivo
arquivo = "data/levantamento_dados.csv"

# Lê toda a planilha
df = pd.read_csv(arquivo, sep=";", encoding="latin1")

# Define as colunas que serão usadas para comparar duplicidade
colunas_para_comparar = [
    "TIPO",
    "TIPO EQUIPAMENTO",
    "EQUIPAMENTO",
    "MARCA",
    "TIPO DE SERVIÇO",
    "COMPLEMENTO",
    "RESOLUÇÃO"
]

# Remove linhas duplicadas com base apenas nas colunas analisadas, mantendo a primeira ocorrência
df = df.drop_duplicates(subset=colunas_para_comparar, keep='first')

# Convert as colunas de texto para o formato de data/hora (datetime)..
df['HORARIO INICIO'] = pd.to_datetime(df['HORARIO INICIO'], errors='coerce')
df['HORARIO FIM'] = pd.to_datetime(df['HORARIO FIM'], errors='coerce')

#  Calcula a diferença e criar a nova coluna "TEMPO".
df['TEMPO'] = ((df['HORARIO FIM'] - df['HORARIO INICIO']).dt.total_seconds() / 3600).round(2)

df.to_csv("data/resultado_sem_duplicatas.csv", index=False)
df.to_excel("data/resultado_sem_duplicatas.xlsx", index=False)
