import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
import pandas as pd


# Função para colocar as datas em formatos de datas
def date_date(df):
    # Filtra as colunas que contêm "dt" no nome
    colunas_com_dt = [col for col in df.columns if 'dt' in col]
    for i in colunas_com_dt:
        df[i] = pd.to_datetime(df[i], format='%d/%m/%Y  %H:%M', errors='coerce')
    return df


# Função para transformar anos em strings
def year_str(df):
    # Filtra as colunas que contêm "dt" no nome
    colunas_com_dt = [col for col in df.columns if 'dt' in col]
    for i in colunas_com_dt:
        df['Ano_'+str(i)] = df[i].apply(lambda x: 0 if pd.isnull(x) else x.strftime('%Y'))
    return df



# Funções para transformar em valores e percentuais em string no formato brasileiro
def brazil_vlr(x, y=0):
    return locale.format_string(f"%.{y}f", x, grouping=True)

def brazil_per(x, y=0):
    return locale.format_string(f"%.{y}f%%", x, grouping=True)



# Transformação para Bilhões e para Milhões
subtractB = 1e9 # Bilhões
subtractM = 1e6 # Milhões

# Casas decimais
decimais_vlr = 1
decimais_per = 1



# Dicionário de cores - Ascom/Seaid
colors_list = [
    '#1D3C69', 
    '#FFA300', 
    '#FFD000', 
    '#183EFF', '#66E266', '#00D000', '#FF0000', '#000000'
]