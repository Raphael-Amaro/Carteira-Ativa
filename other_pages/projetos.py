import pandas as pd
import numpy as np
import locale
import os
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
from modules.conf import brazil_vlr, subtractM, decimais_vlr, brazil_per, decimais_per, subtractB, colors_list
import streamlit as st


def projetos_tabelas(filtered_df, distinct_df):
    novo_df = (
        filtered_df
        .set_index('nmProjeto')  # Criar índice com nmProjeto
        [['Regiao', 'nmUnidadeFederal', 'nmAbrangenciaNacional', 'sgFonte', 'nmSetor', 'VlDolar', 'CpVlDolar']]  # Selecionar colunas desejadas
        .copy()  # Criar cópia para evitar alterações no original
        .sort_values(by=['Regiao', 'nmUnidadeFederal', 'nmAbrangenciaNacional'])  # Ordenar pelo valor desejado
        .rename(columns={
            'Regiao': 'Região',
            'nmUnidadeFederal': 'UF',
            'nmAbrangenciaNacional': 'Esfera',
            'sgFonte': 'Fonte',
            'nmSetor': 'Setor',
            'VlDolar': 'Valor (US$)',
            'CpVlDolar': 'Contrapartida (US$)'
        })  # Renomear as colunas
    )


    # Definir o nome do índice como "Fase"
    novo_df.index.name = 'Nome do Projeto ou Programa'

    # Remover as linhas com índice igual a '_x000D_'
    novo_df = novo_df.drop('_x000D_', axis=0, errors='ignore')


    # Formatar valores das colunas
    novo_df['Valor (US$)'] = novo_df['Valor (US$)'].apply(
        lambda x: brazil_vlr(x, 0)
    )

    novo_df['Contrapartida (US$)'] = novo_df['Contrapartida (US$)'].apply(
        lambda x: brazil_vlr(x, 0)
    )


    nacional_tab = novo_df[novo_df['Região'] == "Nacional"].drop(columns=['Região']).fillna('')
    CO_tab = novo_df[novo_df['Região'] == "Centro Oeste"].drop(columns=['Região']).fillna('')
    NO_tab = novo_df[novo_df['Região'] == "Nordeste"].drop(columns=['Região']).fillna('')
    NOR_tab = novo_df[novo_df['Região'] == "Norte"].drop(columns=['Região']).fillna('')
    SU_tab = novo_df[novo_df['Região'] == "Sudeste"].drop(columns=['Região']).fillna('')
    S_tab = novo_df[novo_df['Região'] == "Sul"].drop(columns=['Região']).fillna('')

    return nacional_tab, CO_tab, NO_tab, NOR_tab, SU_tab, S_tab






def projetos(filtered_df, distinct_df):
    st.header("Lista de Projetos e Programas por Região", divider='gray')

    if 'TEXT_PROJETOS' in locals():
        pass  # Ou outra ação
    else:
        # data_text_end_y, fig = uf_chart_interativo(filtered_df_sem_federal)
        # TEXT_PROJETOS, F_TAB, f_tab_0sum, f_tab_1sum, f_tab_2sum = fontes(filtered_df, distinct_df)
        TEXT_PROJETOS = ""
        
    nacional_tab, CO_tab, NO_tab, NOR_tab, SU_tab, S_tab  = projetos_tabelas(filtered_df, distinct_df)

    with st.container():

        # st.write(
        #     f"""
        #     <div style="text-align: justify;">
        #         {TEXT_PROJETOS}
        #     </div>
        #     """,
        #     unsafe_allow_html=True
        # )

        st.write("")  # Linhas em branco para espaçamento
        st.write("")

        nacional, CO, NO, NOR, SU, S  = st.tabs([":flag-br: Nacional", "Centro Oeste", "Nordeste", "Norte", "Sudeste", "Sul"])

        with nacional:
            # col1, col2, col3 = st.columns([0.20, 0.6, 0.20])
            # with col2:
            st.markdown(
                '<strong>Gráfico</strong> - Lista de Projetos e Programas</p>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<p style="margin-top: -20px;"><strong>Fonte:</strong> SUFIN/SEAID/MPO</p>',
                unsafe_allow_html=True
            )
            st.dataframe(nacional_tab)
        
        with CO:
            # col1, col2, col3 = st.columns([0.20, 0.6, 0.20])
            # with col2:
            st.markdown(
                '<strong>Tabela</strong> - Lista de Projetos e Programas</p>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<p style="margin-top: -20px;"><strong>Fonte:</strong> SUFIN/SEAID/MPO</p>',
                unsafe_allow_html=True
            )
            st.dataframe(CO_tab)
        
        with NO:
            # col1, col2, col3 = st.columns([0.20, 0.6, 0.20])
            # with col2:
            st.markdown(
                '<strong>Tabela</strong> - Lista de Projetos e Programas</p>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<p style="margin-top: -20px;"><strong>Fonte:</strong> SUFIN/SEAID/MPO</p>',
                unsafe_allow_html=True
            )
            st.dataframe(NO_tab)     

        with NOR:
            # col1, col2, col3 = st.columns([0.20, 0.6, 0.20])
            # with col2:
            st.markdown(
                '<strong>Tabela</strong> - Lista de Projetos e Programas</p>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<p style="margin-top: -20px;"><strong>Fonte:</strong> SUFIN/SEAID/MPO</p>',
                unsafe_allow_html=True
            )
            st.dataframe(NOR_tab)     

        with SU:
            # col1, col2, col3 = st.columns([0.20, 0.6, 0.20])
            # with col2:
            st.markdown(
                '<strong>Tabela</strong> - Lista de Projetos e Programas</p>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<p style="margin-top: -20px;"><strong>Fonte:</strong> SUFIN/SEAID/MPO</p>',
                unsafe_allow_html=True
            )
            st.dataframe(SU_tab)     

        with S:
            # col1, col2, col3 = st.columns([0.20, 0.6, 0.20])
            # with col2:
            st.markdown(
                '<strong>Tabela</strong> - Lista de Projetos e Programas</p>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<p style="margin-top: -20px;"><strong>Fonte:</strong> SUFIN/SEAID/MPO</p>',
                unsafe_allow_html=True
            )
            st.dataframe(S_tab)     