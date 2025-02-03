import pandas as pd
import numpy as np
import locale
import os
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
from modules.conf import brazil_vlr, subtractM, decimais_vlr, brazil_per, decimais_per, subtractB, colors_list
import streamlit as st
import plotly.graph_objects as go





def fontes(filtered_df, distinct_df):
    # Criar o dataframe 'carteira_tab' sem perder a coluna 'sgFonte'
    carteira_tab = pd.DataFrame({
        'Número de Projetos': distinct_df.groupby('sgFonte')['cdCartaConsulta'].count(),
        'Valor de Empréstimo': filtered_df.groupby('sgFonte')['VlDolar'].sum(),
        'Valor de Contrapartida': filtered_df.groupby('sgFonte')['CpVlDolar'].sum()
    }).reset_index()  # Garantir que 'sgFonte' não seja removido como índice

    carteira_tab.fillna(0, inplace=True)

    # Remover as fases com valor zero em 'Valor de Empréstimo'
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]

    # Ordenar pelo valor de 'Valor de Empréstimo'
    carteira_tab.sort_values(by='Valor de Empréstimo', ascending=False, inplace=True)

    # Selecionar os 13 fontes com maior valor em 'Valor de Empréstimo'
    top_fontes = carteira_tab.nlargest(11, 'Valor de Empréstimo')['sgFonte'].tolist()
    carteira_tab['sgFonte'] = carteira_tab['sgFonte'].apply(lambda x: x if x in top_fontes else 'Outras')

    # Agrupar os fontes restantes como "Outros"
    carteira_tab = carteira_tab.groupby('sgFonte', as_index=False).sum()

    # Aplicar o cálculo do percentual formatado
    carteira_tab['Empréstimo / Total (%)'] = (
        carteira_tab['Valor de Empréstimo'] / carteira_tab['Valor de Empréstimo'].sum()
    )

    # Remover as fases com valor zero em 'Valor de Empréstimo'
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]

    # Ordenar as fontes pelo valor de 'Valor de Empréstimo'
    carteira_tab.sort_values(by='Valor de Empréstimo', ascending=False, inplace=True)

    # Garantir que a linha "Outras" seja a última
    carteira_tab = pd.concat([
        carteira_tab[carteira_tab['sgFonte'] != 'Outras'],  # Todas as linhas exceto "Outras"
        carteira_tab[carteira_tab['sgFonte'] == 'Outras']   # A linha "Outras"
    ])

    # Preservar 'sgFonte' no índice para evitar erros posteriores
    carteira_tab.set_index('sgFonte', inplace=True)


     # Adicionar linha com a soma dos valores
    sum_row = pd.DataFrame({
        'Número de Projetos': [carteira_tab['Número de Projetos'].sum()],
        'Valor de Empréstimo': [carteira_tab['Valor de Empréstimo'].sum()],
        'Valor de Contrapartida': [carteira_tab['Valor de Contrapartida'].sum()],
        'Empréstimo / Total (%)': [carteira_tab['Empréstimo / Total (%)'].sum()]
    }, index=['Total'])

    # Concatenar a linha de soma ao DataFrame original
    carteira_tab = pd.concat([carteira_tab, sum_row])

    # Definir o nome do índice como "Fase"
    carteira_tab.index.name = 'Fonte'


    # Duplicar tabela para transformar a nova tab em string
    carteira_tab_str = carteira_tab.copy()
    carteira_tab_str['Número de Projetos'] = carteira_tab_str['Número de Projetos'].apply(lambda x: brazil_vlr(x, 0))
    carteira_tab_str['Valor de Empréstimo'] = carteira_tab_str['Valor de Empréstimo'].apply(
        lambda x: brazil_vlr(x / subtractM, decimais_vlr))
    carteira_tab_str['Valor de Contrapartida'] = carteira_tab_str['Valor de Contrapartida'].apply(
        lambda x: brazil_vlr(x / subtractM, decimais_vlr))
    
    carteira_tab_str['Empréstimo / Total (%)'] = carteira_tab_str['Empréstimo / Total (%)'].apply(
        lambda x: brazil_per(x * 100, decimais_per)
    )

    carteira_tab = carteira_tab.drop(index="Total", errors="ignore")

    # Gerar texto descritivo
    lista_carteira = []
    for i in range(len(carteira_tab)):
        percentual = brazil_per((carteira_tab.iloc[i]['Valor de Empréstimo'] / carteira_tab['Valor de Empréstimo'].sum()) * 100, decimais_per)
        if i == 0:
            lista_carteira.append(f"Em âmbito nacional, o valor total dos projetos e programas em Carteira alcançou US$ {brazil_vlr(carteira_tab.iloc[i]['Valor de Empréstimo'] / subtractB, decimais_vlr)} {'bilhões' if (carteira_tab.iloc[i]['Valor de Empréstimo'] / subtractB ) >= 2 else 'bilhão' }, correspondendo a {percentual} do total financeiro. Em termos de alocação regional, as regiões ordenadas pelo montante recebido são as seguintes: ")
        elif i == len(carteira_tab) - 1:
            lista_carteira.append(f"{carteira_tab.index[i]}, US$ {brazil_vlr(carteira_tab.iloc[i]['Valor de Empréstimo'] / subtractB, decimais_vlr)} {'bilhões' if (carteira_tab.iloc[i]['Valor de Empréstimo'] / subtractB ) >= 2 else 'bilhão' } ({percentual}).")
        else:
            lista_carteira.append(f"{carteira_tab.index[i]}, US$ {brazil_vlr(carteira_tab.iloc[i]['Valor de Empréstimo'] / subtractB, decimais_vlr)} {'bilhões' if (carteira_tab.iloc[i]['Valor de Empréstimo'] / subtractB ) >= 2 else 'bilhão' } ({percentual}); ")

    lista_carteira_join = ''.join(lista_carteira)

    return (
         f"Constata-se, na tabela subsequente, a distribuição dos financiamentos externos da Carteira Ativa da Cofiex, devidamente segmentada por fonte de financiamento, evidenciando-se a predominância de determinados agentes financeiros no apoio a projetos e programas da Carteira. "
        f"Nesse contexto, destacam-se o {carteira_tab.index[0]} e o {carteira_tab.index[1]}, que se posicionam como principais fontes contribuintes.",
        # + lista_carteira_join,
        carteira_tab_str,
        brazil_vlr(carteira_tab['Número de Projetos'].sum(), 0),
        brazil_vlr(carteira_tab['Valor de Empréstimo'].sum() / subtractM, decimais_vlr),
        brazil_vlr(carteira_tab['Valor de Contrapartida'].sum() / subtractM, decimais_vlr)
    )









# GRÁFICO
# Dicionário de cores específicas para cada fonte
color_dict = {
    'BID': colors_list[0],
    'BIRD': colors_list[1],
    'CAF': colors_list[2],
    'NDB': colors_list[3],
    'FONPLATA': colors_list[4],
    'Outras': colors_list[5]
}

def fonte_pie_interativo(filtered_df, distinct_df):
    """
    Retorna a figura Plotly (do tipo 'donut') com a distribuição de financiamentos externos
    autorizados por agente financeiro, pronta para exibição no Streamlit.
    """

    # 1) Monta o DataFrame carteira_tab
    carteira_tab = pd.DataFrame({
        'Número de Projetos': distinct_df.groupby('sgFonteResumo')['cdCartaConsulta'].count(),
        'Valor de Empréstimo': filtered_df.groupby('sgFonteResumo')['VlDolar'].sum(),
        'Valor de Contrapartida': filtered_df.groupby('sgFonteResumo')['CpVlDolar'].sum()
    })
    carteira_tab.fillna(0, inplace=True)

    # Remove linhas cujo Valor de Empréstimo é zero
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]

    # Resetar o índice para ter sgFonteResumo como coluna
    carteira_tab.reset_index(inplace=True)  # gera colunas: ['sgFonteResumo','Número de Projetos','Valor de Empréstimo','Valor de Contrapartida']

    # df_plot com apenas ['sgFonteResumo','Valor de Empréstimo'] em bilhões
    df_plot = carteira_tab[['sgFonteResumo', 'Valor de Empréstimo']].copy()
    df_plot['Valor de Empréstimo'] /= subtractB  # converte para Bilhões

    # 2) Preparar dados para o gráfico
    labels = df_plot['sgFonteResumo'].tolist()
    values = df_plot['Valor de Empréstimo'].values

    # 3) Montar a lista de cores a partir de color_dict
    #    Se não existir a fonte no dicionário, usar cor padrão (#d3d3d3)
    marker_colors = [color_dict.get(lbl, '#d3d3d3') for lbl in labels]

    # 4) Criar o donut chart com go.Figure + go.Pie
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,               # Fator "donut"
                # Usando 'pull' para afastar todas as fatias igualmente
                # pull=0.02,  # 0.02 = 2% do raio
                marker=dict(colors=marker_colors, line=dict(color='gray', width=0.8)),
                hovertemplate=(
                    "%{label}<br>"
                    "Empréstimo: %{value:.1f}B<br>"
                    "Percentual: %{percent}<extra></extra>"
                ),
                # textinfo controla o texto mostrado no setor
                # "label+percent" mostraria rótulo e %
                textinfo='percent', 
                textposition='inside'   # texto dentro da fatia
            )
        ]
    )

    # 5) Ajustar layout: título, legenda, margens, etc.
    fig.update_layout(
        # title="Financiamentos Externos por Fonte",
        margin=dict(l=50, r=50, t=30, b=80),
        showlegend=True,  # Se quiser exibir a legenda
        legend=dict(
            orientation='h',
            x=0.5,
            xanchor='center',
            y=-0.1,
            yanchor='top'
        )
    )

    # Opcional: Inserir um texto no centro do donut
    # (substitui a ideia do "círculo central" do Matplotlib)
    fig.update_layout(
        annotations=[dict(
            text="Fontes de Financiamento",
            x=0.5, y=0.5, showarrow=False,
            font_size=12, font_color="dimgray"
        )]
    )

    return fig

# ------------------------------------------
# Exemplo de uso no seu app Streamlit:
#
# def app():
#     fig = fonte_pie_interativo(filtered_df, distinct_df)
#     st.plotly_chart(fig, use_container_width=True)
#
# if __name__ == "__main__":
#     app()







def fonte(filtered_df, distinct_df):
    st.header("Fontes de Financiamento", divider='gray')

    if 'TEXT_FONTE' in locals():
        pass  # Ou outra ação
    else:
        # data_text_end_y, fig = uf_chart_interativo(filtered_df_sem_federal)
        TEXT_FONTE, F_TAB, f_tab_0sum, f_tab_1sum, f_tab_2sum = fontes(filtered_df, distinct_df)
        
    
    with st.container():

        st.write(
            f"""
            <div style="text-align: justify;">
                {TEXT_FONTE}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")  # Linhas em branco para espaçamento
        st.write("")

        tab2, tab1 = st.tabs(["📈 Gráfico", "🗃 Tabela"])

        with tab1:

            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])


            with col2:
                st.markdown(
                    '<strong>Tabela</strong> - Distribuição de financiamentos externos da Carteira Ativa da Cofiex por fonte de financiamento</p>',
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

                st.dataframe(F_TAB)

        
        with tab2:

            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])


            with col2:
                st.markdown(
                    '<strong>Gráfico</strong> - Distribuição de financiamentos externos da Carteira Ativa da Cofiex por fonte de financiamento</p>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<p style="margin-top: -20px;"><strong>Dados em:</strong> Percentual dos valores totais de financiamentos da Carteira da Cofiex</p>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<p style="margin-top: -20px;"><strong>Fonte:</strong> SUFIN/SEAID/MPO</p>',
                    unsafe_allow_html=True
                )

                fig = fonte_pie_interativo(filtered_df, distinct_df)
                st.plotly_chart(fig, use_container_width=True)
