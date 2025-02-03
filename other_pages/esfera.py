import pandas as pd
import numpy as np
import locale
import os
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
from modules.conf import brazil_vlr, subtractM, decimais_vlr, brazil_per, decimais_per, subtractB, colors_list
import streamlit as st
import plotly.graph_objects as go


## Tabela e Texto: Distribuição da Carteira Ativa de acordo com a fase de andamento dos projetos 
def entes_federativos(filtered_df, distinct_df):

    # Continuar com o cálculo
    carteira_tab = pd.DataFrame({
        'Número de Projetos': distinct_df.groupby('nmAbrangenciaNacional')['cdCartaConsulta'].count(), # Não usar distinct
        'Valor de Empréstimo': filtered_df.groupby('nmAbrangenciaNacional')['VlDolar'].sum(),
        'Valor de Contrapartida': filtered_df.groupby('nmAbrangenciaNacional')['CpVlDolar'].sum()
    })
    carteira_tab.fillna(0, inplace=True)

    # Aplicar o cálculo do percentual formatado
    carteira_tab['Empréstimo / Total (%)'] = (
        carteira_tab['Valor de Empréstimo'] / carteira_tab['Valor de Empréstimo'].sum()
    )

    # Remover as fases com valor zero em 'Valor de Empréstimo'
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]

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
    carteira_tab.index.name = 'Ente Federativo'

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

    lista_carteira = []
    for i in range(len(carteira_tab_sorted)):
        percentual = brazil_per((carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / carteira_tab_sorted['Valor de Empréstimo'].sum()) * 100, decimais_per)
        if i == 0:
            lista_carteira.append(f"'{carteira_tab_sorted.index[i]}', a qual representa {percentual} do total de recursos da Carteira. ")
        elif i == len(carteira_tab_sorted) - 1:
            lista_carteira.append(f"e, subsequentemente, pela esfera '{carteira_tab_sorted.index[i]}', que responde por {percentual} dos recursos totais.")
        else:
            lista_carteira.append(f"Esta é seguida pela esfera '{carteira_tab_sorted.index[i]}', com uma participação de {percentual}, ")

    # Une todos os elementos da lista_carteira em uma única string e imprime
    lista_carteira_join = ''.join(lista_carteira)

    return (
        f"Em relação à distribuição dos financiamentos externos da Carteira Ativa da Cofiex entre os entes federativos, observa-se que existe uma predominância da esfera "
        + lista_carteira_join,
        carteira_tab_str,
        brazil_vlr(carteira_tab['Número de Projetos'].sum(), 0),
        brazil_vlr(carteira_tab['Valor de Empréstimo'].sum() / subtractM, decimais_vlr),
        brazil_vlr(carteira_tab['Valor de Contrapartida'].sum() / subtractM, decimais_vlr)
    )

## GRÁFICO

def entes_charts(filtered_df, distinct_df):
    # --- 1) Cálculo dos Dados ---
    carteira_tab = pd.DataFrame({
        'Número de Projetos': distinct_df.groupby('nmAbrangenciaNacional')['cdCartaConsulta'].count(),
        'Valor de Empréstimo': filtered_df.groupby('nmAbrangenciaNacional')['VlDolar'].sum(),
        'Valor de Contrapartida': filtered_df.groupby('nmAbrangenciaNacional')['CpVlDolar'].sum()
    })
    carteira_tab.fillna(0, inplace=True)

    # Calcula porcentagem de cada ente
    total_emprestimo = carteira_tab['Valor de Empréstimo'].sum()
    carteira_tab['Empréstimo / Total (%)'] = carteira_tab['Valor de Empréstimo'] / total_emprestimo
    
    # Filtra entes com valor de empréstimo > 0
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]
    carteira_tab.index.name = 'Ente Federativo'

    categorias = ['Estadual', 'Federal', 'Municipal']
    percentages = {}
    for cat in categorias:
        if cat in carteira_tab.index:
            percentages[cat] = carteira_tab.loc[cat, 'Empréstimo / Total (%)']
        else:
            percentages[cat] = 0

    # --- 2) Definição do grid (ex.: 4 x 25 = 100 quadrados) ---
    rows = 4
    columns = 25
    total_tiles = rows * columns  # 4 * 25 = 100

    # Distribui os quadradinhos para cada categoria, de acordo com a %:
    counts = {}
    for cat in categorias:
        counts[cat] = int(round(percentages[cat] * total_tiles))

    # Ajusta possíveis discrepâncias de arredondamento
    total_assigned = sum(counts.values())
    diff = total_tiles - total_assigned
    if diff != 0:
        # Ajusta na categoria de maior percentual
        max_cat = max(percentages, key=percentages.get)
        counts[max_cat] += diff

    # Cria a "lista" de categorias para cada quadradinho
    assignment = []
    for cat in categorias:
        assignment.extend([cat] * counts[cat])
    # Garante que não ultrapasse o total de quadradinhos
    assignment = assignment[:total_tiles]

    # --- 3) Geração das coordenadas preenchendo VERTICALMENTE ---
    # Preenche cada coluna de cima para baixo, depois segue para a próxima coluna.
    xs, ys, cats = [], [], []
    for i, cat in enumerate(assignment):
        # col = índice da coluna; row = índice da linha
        # i // rows: avança a coluna a cada "rows" quadradinhos
        # i % rows: dentro de cada coluna, avança a linha
        col = i // rows
        row = i % rows
        x_center = col + 0.5
        # Para "inverter" a contagem na vertical (topo = y maior):
        y_center = (rows - 1 - row) + 0.5
        
        xs.append(x_center)
        ys.append(y_center)
        cats.append(cat)

    df_tiles = pd.DataFrame({'x': xs, 'y': ys, 'category': cats})

    # --- 4) Definindo cores e texto de hover ---
    color_map = {
        'Estadual': colors_list[0],   # azul
        'Federal': colors_list[1],    # laranja
        'Municipal': colors_list[2]   # verde
    }
    df_tiles['color'] = df_tiles['category'].map(color_map)
    df_tiles['hover'] = df_tiles['category'].apply(
        lambda cat: f"{cat}: {round(percentages[cat]*100,1)}%"
    )

    # --- 5) Construção do gráfico com Plotly ---
    fig = go.Figure()

    for cat in categorias:
        df_cat = df_tiles[df_tiles['category'] == cat]
        legenda_texto = f"{cat} ({round(percentages[cat]*100,1)}%)"
        fig.add_trace(
            go.Scatter(
                x=df_cat['x'],
                y=df_cat['y'],
                mode='markers',
                marker=dict(
                    symbol='square',
                    size=30,    # Tamanho de cada "quadrado" (ajuste se precisar)
                    line=dict(width=2, color='white'),
                    color=df_cat['color']
                ),
                hovertext=df_cat['hover'],
                hoverinfo='text',
                name=legenda_texto
            )
        )

    # --- 6) Layout e formatação ---
    fig.update_layout(
        # title="ESFERAS - FIGURA 1 (Waffle Chart)",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0, columns]  # 0 a 25
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0, rows]     # 0 a 4
        ),
        plot_bgcolor='white',
        # Definimos width e height para respeitar a proporção de 25:4 ~= 6,25
        width=1250,
        height=200,
        margin=dict(l=30, r=30, t=50, b=50),  # Aumente/diminua conforme precisar
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
            y=-0.15   # Aproxima a legenda do gráfico (valor negativo = pra fora)
        )
    )
    # Garante a proporção 1:1 entre os eixos
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    return fig



def esfera(filtered_df, distinct_df):
    st.header("Entes Federativos", divider='gray')

    if 'TEXT_ENTES' in locals():
        pass  # Ou outra ação
    else:
        TEXT_ENTES, E_TAB, _, _, _ = entes_federativos(filtered_df, distinct_df)
    
    with st.container():
        
        st.write(
            f"""
            <div style="text-align: justify;">
                {TEXT_ENTES}
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
                    '<strong>Tabela</strong> - Distribuição de financiamentos externos da Carteira Ativa da Cofiex entre entes federativos</p>',
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

                st.dataframe(E_TAB)

        with tab2:
            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])


            with col2:
                st.markdown(
                    '<strong>Gráfico</strong> - Distribuição de financiamentos externos da Carteira Ativa da Cofiex entre entes federativos</p>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    '<p style="margin-top: -20px;"><strong>Dados em:</strong> percentual dos valores totais de financiamentos</p>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    '<p style="margin-top: -20px;"><strong>Fonte:</strong> SUFIN/SEAID/MPO</p>',
                    unsafe_allow_html=True
                )

            fig = entes_charts(filtered_df, distinct_df)
            st.plotly_chart(fig, use_container_width=True)
        