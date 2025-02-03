import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import locale
import os
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
from modules.conf import date_date, year_str


# PEGAR AS CONFIGURAÇÕES DO CSS
with open("css/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Carregar dados
from modules.data import carteira_ativa, sem_federal

# Ler dados
df = pd.read_excel('data/data.xlsx', sheet_name='Base')

# Transformar datas em datas
df=date_date(df)

# Transformar anos em strings
df=year_str(df)

# Carteira Ativa
filtered_df, distinct_df = carteira_ativa(df)
# Sem federal
filtered_df_sem_federal, distinct_df_sem_federal = sem_federal(df)


# horizontal menu
selected = option_menu(None, ["Carteira", "Esfera", "Região", "UF", "Setor", "Financiador", "Projetos"], 
    icons=['wallet2', 'layers', 'globe-americas', 'geo-alt', 'ui-checks-grid', 'cash-coin', 'list-task'], 
    menu_icon="cast", default_index=0, orientation="horizontal")

if selected == "Carteira":
    from other_pages.carteira import carteira
    carteira(filtered_df, distinct_df)

elif selected == "Esfera":
    from other_pages.esfera import esfera
    esfera(filtered_df, distinct_df)

elif selected == "Região":
    from other_pages.regiao import regiao
    regiao(filtered_df, distinct_df)

elif selected == "UF":
    from other_pages.uf import uf
    uf(filtered_df_sem_federal, distinct_df_sem_federal)

elif selected == "Setor":
    from other_pages.setor import setor
    setor(filtered_df, distinct_df)

elif selected == "Financiador":
    from other_pages.fonte import fonte
    fonte(filtered_df, distinct_df)

elif selected == "Projetos":
    from other_pages.projetos import projetos
    projetos(filtered_df, distinct_df)

else:
    from other_pages.carteira import carteira
    carteira(filtered_df, distinct_df)