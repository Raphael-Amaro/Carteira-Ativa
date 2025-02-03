import pandas as pd
import numpy as np
import locale
import os
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
from modules.conf import brazil_vlr, subtractM, decimais_vlr, brazil_per, decimais_per, subtractB, colors_list
import streamlit as st
import plotly.graph_objects as go



## Tabela e Texto: Distribuição da Carteira Ativa de acordo com a fase de andamento dos projetos 
def regioes_text(filtered_df, distinct_df):

    # Continuar com o cálculo
    carteira_tab = pd.DataFrame({
        'Número de Projetos': distinct_df.groupby('Regiao')['cdCartaConsulta'].count(), # Não usar distinct
        'Valor de Empréstimo': filtered_df.groupby('Regiao')['VlDolar'].sum(),
        'Valor de Contrapartida': filtered_df.groupby('Regiao')['CpVlDolar'].sum()
    })
    carteira_tab.fillna(0, inplace=True)

    # Aplicar o cálculo do percentual formatado
    carteira_tab['Empréstimo / Total (%)'] = (
        carteira_tab['Valor de Empréstimo'] / carteira_tab['Valor de Empréstimo'].sum()
    )

    # Remover as fases com valor zero em 'Valor de Empréstimo'
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]


    carteira_tab.sort_values(by='Valor de Empréstimo', ascending=False, inplace=True)

    # Nacional sempre em primeiro
    carteira_tab = carteira_tab.loc[['Nacional'] + [idx for idx in carteira_tab.index if idx != 'Nacional']]

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
    carteira_tab.index.name = 'Região'



    # Duplicar tabela para transformar a nova tab em string
    carteira_tab_str = carteira_tab.copy()

    # Formatar valores das colunas
    carteira_tab_str['Número de Projetos'] = carteira_tab_str['Número de Projetos'].apply(
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
    # carteira_tab_sorted = carteira_tab_sorted.drop('Nacional', axis=0)
    # Reordenar o índice para que 'Coco' seja o primeiro
    carteira_tab_sorted = carteira_tab_sorted.loc[['Nacional'] + [idx for idx in carteira_tab_sorted.index if idx != 'Nacional']]


    lista_carteira = []
    for i in range(len(carteira_tab_sorted)):
        percentual = brazil_per((carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / carteira_tab_sorted['Valor de Empréstimo'].sum()) * 100, decimais_per)
        if i == 0:
            lista_carteira.append(f"Em âmbito nacional, o valor total dos projetos e programas em Carteira alcançou US$ {brazil_vlr(carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB, decimais_vlr)} {'bilhões' if (carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB ) >= 2 else 'bilhão' }, correspondendo a {percentual} do total financeiro. Em termos de alocação regional, as regiões ordenadas pelo montante recebido são as seguintes: ")
            
        elif i == len(carteira_tab_sorted) - 1:
            lista_carteira.append(f"{carteira_tab_sorted.index[i]}, US$ {brazil_vlr(carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB, decimais_vlr)} {'bilhões' if (carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB ) >= 2 else 'bilhão' } ({percentual}).")
        else:
            lista_carteira.append(f"{carteira_tab_sorted.index[i]}, US$ {brazil_vlr(carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB, decimais_vlr)} {'bilhões' if (carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB ) >= 2 else 'bilhão' } ({percentual}); ")

   # Une os elementos da lista com espaço entre eles
    lista_carteira_join = ' '.join(lista_carteira)

    # Garante que os números estão corretamente formatados antes da saída final
    return (
        f"Explorando os aspectos geográficos dos projetos e programas da Carteira Ativa da Cofiex, "
        f"a tabela subsequente ilustra a distribuição dos financiamentos externos entre as diversas regiões do país. "
        f"{lista_carteira_join}",
        carteira_tab_str,
        brazil_vlr(carteira_tab['Número de Projetos'].sum(), 0),
        brazil_vlr(carteira_tab['Valor de Empréstimo'].sum() / subtractM, decimais_vlr),
        brazil_vlr(carteira_tab['Valor de Contrapartida'].sum() / subtractM, decimais_vlr)
    )


## GRÁFICO


def regioes_chart(filtered_df, distinct_df):
    # --- 1) Monta o DataFrame carteira_tab ---
    carteira_tab = pd.DataFrame({
        'Número de Projetos': distinct_df.groupby('Regiao')['cdCartaConsulta'].count(),
        'Valor de Empréstimo': filtered_df.groupby('Regiao')['VlDolar'].sum(),
        'Valor de Contrapartida': filtered_df.groupby('Regiao')['CpVlDolar'].sum()
    })
    carteira_tab.fillna(0, inplace=True)

    carteira_tab['Empréstimo / Total (%)'] = (
        carteira_tab['Valor de Empréstimo'] / carteira_tab['Valor de Empréstimo'].sum()
    )

    # Filtra regiões sem valor de empréstimo
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]
    carteira_tab.index.name = 'Regiões'

    # Ordena do maior para o menor
    carteira_tab.sort_values(by='Valor de Empréstimo', ascending=False, inplace=True)

    # --- 2) Prepara o df_plot (valores em Bilhões) ---
    df_plot = carteira_tab[['Valor de Empréstimo']].copy()
    df_plot['Valor de Empréstimo'] /= subtractB  # converter para bilhões

    # Separa "Nacional" das demais, se existir
    df_nacional = df_plot.loc[df_plot.index == "Nacional"]
    df_rest = df_plot.loc[df_plot.index != "Nacional"]

    # (Opcional) reordena df_rest em ordem decrescente, caso ainda não esteja
    df_rest = df_rest.sort_values(by="Valor de Empréstimo", ascending=False)

    # --- 3) Definir a ordem categórica: Nacional primeiro, depois as demais ---
    x_labels = []
    if not df_nacional.empty:
        x_labels.append("Nacional")                # força 'Nacional' em primeiro
    x_labels.extend(df_rest.index.tolist())        # depois as demais

    # --- 4) Criar a figura e adicionar dois traces (um p/ Nacional e outro p/ resto) ---
    fig = go.Figure()

    # Trace das regiões (exceto Nacional) - cor principal = colors_list[0]
    if not df_rest.empty:
        x_rest = df_rest.index.tolist()
        y_rest = df_rest["Valor de Empréstimo"].values
        text_rest = [f"{brazil_vlr(v, decimais_vlr)}B" for v in y_rest]

        fig.add_trace(
            go.Bar(
                x=x_rest,
                y=y_rest,
                text=text_rest,
                textposition='outside',
                marker_color=colors_list[0],
                name="Empréstimos",
                hovertemplate="Região: %{x}<br>Empréstimo: %{y:.1f}B<extra></extra>"
            )
        )

    # Trace para "Nacional" (se existir), cor diferente, sem legenda extra
    if not df_nacional.empty:
        x_nac = df_nacional.index.tolist()
        y_nac = df_nacional["Valor de Empréstimo"].values
        text_nac = [f"{brazil_vlr(v, decimais_vlr)}B" for v in y_nac]

        fig.add_trace(
            go.Bar(
                x=x_nac,
                y=y_nac,
                text=text_nac,
                textposition='outside',
                marker_color=colors_list[1],
                showlegend=False,
                hovertemplate="Região: %{x}<br>Empréstimo: %{y:.1f}B<extra></extra>"
            )
        )

    # --- 5) Linha da média (todas as regiões + Nacional, se existir) ---
    all_y = df_plot['Valor de Empréstimo'].values
    media = all_y.mean() if len(all_y) > 0 else 0

    fig.add_hline(
        y=media,
        line_color=colors_list[0],
        line_dash="dash",
        annotation_text=f"Média ({brazil_vlr(media, decimais_vlr)}B)",
        annotation_position="top right",
        annotation_font_color=colors_list[0]
    )
    # Trace invisível para aparecer na legenda
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color=colors_list[0], dash="dash"),
            name=f"Média ({brazil_vlr(media, decimais_vlr)}B)"
        )
    )

    # --- 6) Ajustes de layout ---
    # Força a ordem categórica do eixo x
    fig.update_xaxes(
        showgrid=False,
        categoryorder='array',
        categoryarray=x_labels  # Coloca 'Nacional' em primeiro
    )
    fig.update_yaxes(
    showgrid=False,
    showticklabels=False  # <--- desabilita os números (ticks) do eixo y
)

    # Ajusta range do eixo Y (para dar folga)
    if len(all_y) > 0:
        max_bar = max(all_y)
        fig.update_yaxes(range=[0, max_bar * 1.2])

    # Ajusta margens: reduz o topo (t=30)
    fig.update_layout(
        # title="Empréstimos por Região (em Bilhões)",
        # xaxis=dict(title="Regiões"),
        # yaxis=dict(title="Valor de Empréstimo (B)"),
        margin=dict(l=50, r=50, t=30, b=50),
        width=800,   # <--- define a largura total do gráfico em pixels
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.2,   # abaixo do gráfico
            yanchor="top"
        )
    )

    # Deixa os rótulos do texto acima das barras com tamanho 12
    fig.update_traces(textfont_size=12)

    return fig



def regiao(filtered_df, distinct_df):
    st.header("Regiões", divider='gray')

    if 'TEXT_REGIOES' in locals():
        pass  # Ou outra ação
    else:
        TEXT_REGIOES, R_TAB, _, _, _ = regioes_text(filtered_df, distinct_df)
    
    with st.container():
        st.write(
            f"""
            <div style="text-align: justify;">
                {TEXT_REGIOES}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")  # Linhas em branco para espaçamento
        st.write("")

        tab2, tab1 = st.tabs(["📈 Gráfico", "🗃 Tabela"])

        with tab1:

                # Cria três colunas (lateral, central, lateral)
            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])

            with col2:

                st.markdown(
                    '<strong>Tabela</strong> - Distribuição de financiamentos externos da Carteira Ativa da Cofiex entre regiões</p>',
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

                st.dataframe(R_TAB)

        
        with tab2:


                # Cria três colunas (lateral, central, lateral)
            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])


            with col2:

                st.markdown(
                    '<strong>Gráfico</strong> - Distribuição de financiamentos externos da Carteira Ativa da Cofiex entre regiões</p>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<p style="margin-top: -20px;"><strong>Dados em:</strong> US$ bilhões</p>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<p style="margin-top: -20px;"><strong>Fonte:</strong> SUFIN/SEAID/MPO</p>',
                    unsafe_allow_html=True
                )
                fig_regioes = regioes_chart(filtered_df, distinct_df)
                st.plotly_chart(fig_regioes, use_container_width=True)

            