import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import locale
import os
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')



# CONFIGURAR AS DEFINIÇÕES DA PAGINA
st.set_page_config(
    page_title="Cosid - Coordenação de Sistemas e Dados",
    # page_icon=img,
    page_icon="images/icon.ico",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# PEGAR AS CONFIGURAÇÕES DO CSS
with open("css/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



pages = {
    "📊 Relatórios": [
        st.Page("other_pages/Carteira_ativa.py", title="📈 Carteira Ativa - Cofiex"),
    ],
    "_" * 42: "",
    "📂 Coordenação de Sistemas e Dados": [
        st.Page("other_pages/Contato.py", title="📞 Contato"),
    ],
    "⚙️ Configurações": [
        st.Page("other_pages/Login.py", title="🔐 Entrar"),
    ],
}

pg = st.navigation(pages)

pg.run()

st.sidebar.caption("Dados atualizado em: 03/02/2025")


import base64
# Caminho do arquivo enviado (fundo)
image_path = "images/SEAID_LOGO_MPO_BRASIL_PT_H_Cor_FundoBranco.svg"

# Função para converter imagem em Base64
def get_base64_of_image(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode()

# Converte a imagem para Base64
base64_image = get_base64_of_image(image_path)

# Aplicando CSS com a imagem de fundo em Base64
css_code = f"""
<style>
.stApp {{
    background-image: url("data:image/svg+xml;base64,{base64_image}");
    background-size: 25% auto;  /* Reduz a largura para 50% e mantém altura automática */
    background-repeat: no-repeat;
    background-position: bottom center;  /* Mantém a imagem na parte inferior */
}}
</style>
"""

st.markdown(css_code, unsafe_allow_html=True)



# Adicionando logo e icone do Meu principal
st.logo('images/SEAID_LOGO_PT_Cor_FundoBranco.svg', size="large", icon_image='images/icone.svg')




