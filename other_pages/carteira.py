import pandas as pd
import numpy as np
import locale
import os
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
from modules.conf import brazil_vlr, subtractM, decimais_vlr, brazil_per, decimais_per, subtractB
import streamlit as st



## Tabela e Texto: Distribuição da Carteira Ativa de acordo com a fase de andamento dos projetos 
def carteira_ativa_tab(filtered_df, distinct_df):
    # Combinar as fases em 'Em Negociação'
    def ajustar_fases(fase):
        if fase in ['Aguardando negociação', 'Negociação agendada', 'Em negociação']:
            return 'Em Negociação'
        return fase

    # Ajustar as fases nos DataFrames
    filtered_df.loc[:, 'deFase'] = filtered_df['deFase'].apply(ajustar_fases)
    # distinct_df.loc[:, 'deFase'] = distinct_df['deFase'].apply(ajustar_fases)

    # Continuar com o cálculo
    carteira_tab = pd.DataFrame({
        'Número de Operações': filtered_df.groupby('deFase')['cdCartaConsulta'].count(), # Não usar distinct
        'Valor de Empréstimo': filtered_df.groupby('deFase')['VlDolar'].sum(),
        'Valor de Contrapartida': filtered_df.groupby('deFase')['CpVlDolar'].sum()
    }).reindex(
        ['Aprovada COFIEX', 'Em preparação', 'Em Negociação', 'Aguardando Assinatura', 'Em execução'],
        fill_value=0
    )

    carteira_tab.fillna(0, inplace=True)

    # Remover as fases com valor zero em 'Valor de Empréstimo'
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]

    # Aplicar o cálculo do percentual formatado
    carteira_tab['Empréstimo / Total (%)'] = (
        carteira_tab['Valor de Empréstimo'] / carteira_tab['Valor de Empréstimo'].sum()
    )

    # Adicionar linha com a soma dos valores
    sum_row = pd.DataFrame({
        'Número de Operações': [carteira_tab['Número de Operações'].sum()],
        'Valor de Empréstimo': [carteira_tab['Valor de Empréstimo'].sum()],
        'Valor de Contrapartida': [carteira_tab['Valor de Contrapartida'].sum()],
        'Empréstimo / Total (%)': [carteira_tab['Empréstimo / Total (%)'].sum()]
    }, index=['Total'])

    # Concatenar a linha de soma ao DataFrame original
    carteira_tab = pd.concat([carteira_tab, sum_row])

    # Definir o nome do índice como "Fase"
    carteira_tab.index.name = 'Fase'

    # Duplicar tabela para transformar a nova tab em string
    carteira_tab_str = carteira_tab.copy()

    # Formatar valores das colunas
    carteira_tab_str['Número de Operações'] = carteira_tab_str['Número de Operações'].apply(
        lambda x: brazil_vlr(x, 0)
    )

    # Formatar valores das colunas
    carteira_tab_str['Valor de Empréstimo'] = carteira_tab_str['Valor de Empréstimo'].apply(
        lambda x: brazil_vlr(x / subtractM, decimais_vlr)
    )

    carteira_tab_str['Valor de Contrapartida'] = carteira_tab_str['Valor de Contrapartida'].apply(
        lambda x: brazil_vlr(x / subtractM, decimais_vlr)
    )

    carteira_tab_str['Empréstimo / Total (%)'] = carteira_tab_str['Empréstimo / Total (%)'].apply(
        lambda x: brazil_per(x * 100, decimais_per)
    )

    # Ordenar as fases pelo valor de 'Valor de Empréstimo' em ordem decrescente
    carteira_tab_sorted = carteira_tab.drop(index="Total", errors="ignore")
    carteira_tab_sorted = carteira_tab_sorted.sort_values(by='Valor de Empréstimo', ascending=False)

    lista_carteira = []
    for i in range(len(carteira_tab_sorted)):
        percentual = brazil_per((carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / carteira_tab_sorted['Valor de Empréstimo'].sum()) * 100, decimais_per)
        if i == 0:
            lista_carteira.append(f"Deste total financeiro, {percentual} está associado a projetos na fase '{carteira_tab_sorted.index[i]}'; ")
        elif i == len(carteira_tab_sorted) - 1:
            lista_carteira.append(f"e os {percentual} restantes a projetos na fase '{carteira_tab_sorted.index[i]}', conforme detalhado na tabela apresentada a seguir.")
        else:
            lista_carteira.append(f"{percentual} a projetos na fase '{carteira_tab_sorted.index[i]}'; ")

    # Une todos os elementos da lista_carteira em uma única string e imprime
    lista_carteira_join = ''.join(lista_carteira)

    return (
        f"A carteira ativa da Cofiex compreende, atualmente, um total de {brazil_vlr(carteira_tab.loc[carteira_tab.index != 'Total', 'Número de Operações'].sum(), 0)} operações de crédito externo, "
        f"cujo montante financeiro agregado alcança a expressiva soma de US$ {brazil_vlr(carteira_tab.loc[carteira_tab.index != 'Total', 'Valor de Empréstimo'].sum() / subtractB, decimais_vlr)} {('bilhões' if (carteira_tab.loc[carteira_tab.index != 'Total','Valor de Empréstimo'].sum() / subtractB)>=2 else 'bilhão')}. "
        + lista_carteira_join,
        carteira_tab_str
    )

# def style_dataframe(df, alignments: dict) -> str:
#     """
#     Aplica estilos de alinhamento em colunas específicas do DataFrame.

#     Parâmetros:
#       - df: DataFrame do pandas.
#       - alignments: dicionário onde a chave é o nome da coluna e o valor é a string
#         de alinhamento ('left', 'center' ou 'right').

#     Retorna:
#       - HTML com o DataFrame estilizado.
#     """
#     styled = df.style
#     for coluna, alinhamento in alignments.items():
#         styled = styled.set_properties(subset=[coluna], **{'text-align': alinhamento})
#     return styled.to_html()

# # Define os alinhamentos desejados para cada coluna
# alinhamentos = {
#     'Número de Operações': 'center',  # Centraliza a coluna 1
#     'Valor de Empréstimo': 'right',   # Alinha à direita a coluna 2
#     'Valor de Contrapartida': 'right'    # Alinha à direita a coluna 3
# }




def carteira(filtered_df, distinct_df):
    st.header("Carteira Ativa de Projetos e Programas", divider='gray')

    if 'TEXT_CARTEIRA_ATIVA' in locals():
        pass  # Ou outra ação
    else:
        TEXT_CARTEIRA_ATIVA, CA_TAB = carteira_ativa_tab(filtered_df, distinct_df)


    
    
    with st.container():
        
        st.write(
            f"""
            <div style="text-align: justify;">
                {TEXT_CARTEIRA_ATIVA}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.write("")  # Linhas em branco para espaçamento
        st.write("")
        st.write("")
        st.write("")
        # tab1, tab2 = st.tabs(["📈 Gráfico", "🗃 Tabela"])



# <p style="margin-bottom: -5px;">
        col1, col2, col3 = st.columns([0.3, 0.4, 0.3])


        with col2:
            st.markdown(
                '<strong>Tabela</strong> - Distribuição da Carteira Ativa de acordo com a fase de andamento das operações</p>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<p style="margin-top: -20px;"><strong>Dados em:</strong> unidade e US$ milhões</p>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<p style="margin-top: -20px;"><strong>Fonte:</strong> SUFIN/SEAID/MPO</p>',
                unsafe_allow_html=True
            )


            

            # Exibe o DataFrame estilizado no Streamlit
            # st.markdown(style_dataframe(CA_TAB, alinhamentos), unsafe_allow_html=True)
            st.dataframe(CA_TAB)
            # Adicionar uma nota colada na tabela e com fonte menor
            st.markdown(
                '<p style="font-size: 12px; color: gray; margin-top: -20px;">'
                'Nota: Um programa ou projeto pode contemplar mais de uma operação de crédito externo.</p>',
                unsafe_allow_html=True
            )
            