import pandas as pd
import numpy as np
import locale
import os
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
from modules.conf import brazil_vlr, subtractM, decimais_vlr, brazil_per, decimais_per, subtractB, colors_list
import streamlit as st
import plotly.graph_objects as go
import textwrap



## Tabela e Texto: Distribuição da Carteira Ativa de acordo com a fase de andamento dos projetos 
def setores(filtered_df, distinct_df):

    # Continuar com o cálculo
    carteira_tab = pd.DataFrame({
        'Número de Projetos': distinct_df.groupby('nmSetor')['cdCartaConsulta'].count(), # Não usar distinct
        'Valor de Empréstimo': filtered_df.groupby('nmSetor')['VlDolar'].sum(),
        'Valor de Contrapartida': filtered_df.groupby('nmSetor')['CpVlDolar'].sum()
    })
    carteira_tab.fillna(0, inplace=True)

    # Aplicar o cálculo do percentual formatado
    carteira_tab['Empréstimo / Total (%)'] = (
        carteira_tab['Valor de Empréstimo'] / carteira_tab['Valor de Empréstimo'].sum()
    )

    # Remover as fases com valor zero em 'Valor de Empréstimo'
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]

    carteira_tab.sort_values(by='Valor de Empréstimo', ascending=False, inplace=True)


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
    carteira_tab.index.name = 'Setor'



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

    credito = (
        "Cumpre salientar que o setor de Crédito abrange as instituições responsáveis pela captação de empréstimos, incluindo bancos de desenvolvimento de âmbito nacional e regional, bem como agências de fomento, "
        "sendo os recursos, em etapa subsequente, alocados de forma estratégica a setores prioritários, tais como saúde, educação, infraestrutura, apoio ao desenvolvimento do setor privado, iniciativas voltadas ao meio ambiente, dentre outras áreas de relevância. "
    )


    lista_carteira = []
    for i in range(len(carteira_tab_sorted)):
        percentual = brazil_per((carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / carteira_tab_sorted['Valor de Empréstimo'].sum()) * 100, decimais_per)
        if i == 0:
            lista_carteira.append(f"{carteira_tab_sorted.index[i]} com um montante de US$ {brazil_vlr(carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB, decimais_vlr)} {'bilhões' if (carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB ) >= 2 else 'bilhão' }, representando {percentual} do total de recursos da Carteira. { credito if carteira_tab_sorted.index[i] == 'Crédito' else '' }A ordenação dos setores, de acordo com o montante de recursos recebidos, é apresentada a seguir: ")
            
        elif i == len(carteira_tab_sorted) - 1:
            lista_carteira.append(f"{carteira_tab_sorted.index[i]}, US$ {brazil_vlr(carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB, decimais_vlr)} {'bilhões' if (carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB ) >= 2 else 'bilhão' } ({percentual}).")
        else:
            lista_carteira.append(f"{carteira_tab_sorted.index[i]}, US$ {brazil_vlr(carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB, decimais_vlr)} {'bilhões' if (carteira_tab_sorted.iloc[i]['Valor de Empréstimo'] / subtractB ) >= 2 else 'bilhão' } ({percentual}); ")

    # Une todos os elementos da lista_carteira em uma única string e imprime
    lista_carteira_join = ''.join(lista_carteira)

    return (
        f"Apresenta-se, na tabela subsequente, a distribuição dos financiamentos externos da Carteira Ativa da Cofiex por setor. Observa-se que o setor que mais captou recursos corresponde ao de "
        
        + lista_carteira_join,
        carteira_tab_str,
        brazil_vlr(carteira_tab['Número de Projetos'].sum(), 0),
        brazil_vlr(carteira_tab['Valor de Empréstimo'].sum() / subtractM, decimais_vlr),
        brazil_vlr(carteira_tab['Valor de Contrapartida'].sum() / subtractM, decimais_vlr)
    )



## GRÁFICO

def wrap_labels(labels, width=15):
    """
    Envolve/“quebra” cada rótulo longo em múltiplas linhas
    (substitui '\n' por '<br>' para Plotly).
    """
    wrapped = []
    for lbl in labels:
        w = textwrap.fill(str(lbl), width=width)    # insere '\n'
        wrapped.append(w.replace('\n', '<br>'))     # troca '\n' por '<br>'
    return wrapped

def setores_chart(filtered_df, distinct_df):
    # --- 1) Monta o DataFrame carteira_tab ---
    carteira_tab = pd.DataFrame({
        'Número de Projetos': distinct_df.groupby('nmSetor')['cdCartaConsulta'].count(),
        'Valor de Empréstimo': filtered_df.groupby('nmSetor')['VlDolar'].sum(),
        'Valor de Contrapartida': filtered_df.groupby('nmSetor')['CpVlDolar'].sum()
    })
    carteira_tab.fillna(0, inplace=True)

    carteira_tab['Empréstimo / Total (%)'] = (
        carteira_tab['Valor de Empréstimo'] / carteira_tab['Valor de Empréstimo'].sum()
    )

    # Filtra setores sem valor de empréstimo
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]

    # Reseta o índice para ter 'nmSetor' como coluna
    carteira_tab.reset_index(inplace=True)  # gera colunas ['nmSetor', 'Número de Projetos', ...]

    # --- 2) Monta df_plot (valores em bilhões) ---
    df_plot = carteira_tab[['nmSetor', 'Valor de Empréstimo']].copy()
    df_plot['Valor de Empréstimo'] /= subtractB  # converter para bilhões

    # Seleciona top 5 setores, o resto vira 'Outros'
    top_setores = df_plot.nlargest(5, 'Valor de Empréstimo')['nmSetor'].tolist()
    df_plot['nmSetor'] = df_plot['nmSetor'].apply(lambda x: x if x in top_setores else 'Outros')

    # Agrupa 'Outros'
    df_plot = df_plot.groupby('nmSetor', as_index=False).sum()

    # Separa "Outros" das demais
    df_outros = df_plot[df_plot['nmSetor'] == "Outros"]
    df_rest = df_plot[df_plot['nmSetor'] != "Outros"].sort_values(by='Valor de Empréstimo', ascending=False)

    # Define a ordem: Outros primeiro, depois o restante
    # (se quiser "Outros" no final, mude a concatenação)
    x_labels = []
    if not df_outros.empty:
        x_labels.append("Outros")
    x_labels.extend(df_rest['nmSetor'].tolist())

    # --- 3) Cria a figura e adiciona DOIS traces ---
    fig = go.Figure()

    # (a) Trace para "Outros" (cor = colors_list[1], sem legenda extra)
    if not df_outros.empty:
        x_outros = df_outros['nmSetor'].tolist()  # geralmente será ["Outros"]
        y_outros = df_outros['Valor de Empréstimo'].values
        text_outros = [f"{brazil_vlr(v, decimais_vlr)}B" for v in y_outros]

        fig.add_trace(
            go.Bar(
                x=x_outros,
                y=y_outros,
                text=text_outros,
                textposition='outside',
                marker_color=colors_list[1],  # cor diferente
                showlegend=False,             # não criar item extra na legenda
                hovertemplate="Setor: %{x}<br>Empréstimo: %{y:.1f}B<extra></extra>"
            )
        )

    # (b) Trace para os demais
    if not df_rest.empty:
        x_rest = df_rest['nmSetor'].tolist()
        y_rest = df_rest['Valor de Empréstimo'].values
        text_rest = [f"{brazil_vlr(v, decimais_vlr)}B" for v in y_rest]

        fig.add_trace(
            go.Bar(
                x=x_rest,
                y=y_rest,
                text=text_rest,
                textposition='outside',
                marker_color=colors_list[0],  # cor principal
                name="Empréstimos",
                hovertemplate="Setor: %{x}<br>Empréstimo: %{y:.1f}B<extra></extra>"
            )
        )

    # --- 4) Linha da média ---
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
    # Scatter "invisível" para aparecer na legenda
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color=colors_list[0], dash="dash"),
            name=f"Média ({brazil_vlr(media, decimais_vlr)}B)"
        )
    )

    # --- 5) Quebrar rótulos do eixo x ---
    wrapped_x_labels = wrap_labels(x_labels, width=15)

    # Forçamos essa ordem categórica e usamos "wrapped_x_labels" como ticktext
    fig.update_xaxes(
        tickvals=x_labels,
        ticktext=wrapped_x_labels,
        showgrid=False
    )
    fig.update_yaxes(showgrid=False)

    # Ajusta range do eixo y (dar folga acima)
    if len(all_y) > 0:
        max_bar = max(all_y)
        fig.update_yaxes(range=[0, max_bar * 1.2])

    # Layout final (largura, margem, legenda)
    fig.update_layout(
        margin=dict(l=50, r=50, t=30, b=80),
        width=800,
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.2,
            yanchor="top"
        )
    )

    fig.update_traces(textfont_size=12)

    return fig




def setor(filtered_df, distinct_df):
    st.header("Setores", divider='gray')

    if 'TEXT_SETOR' in locals():
        pass  # Ou outra ação
    else:
        # data_text_end_y, fig = uf_chart_interativo(filtered_df_sem_federal)
        TEXT_SETOR, S_TAB, s_tab_0sum, s_tab_1sum, s_tab_2sum = setores(filtered_df, distinct_df)
        
    
    with st.container():

        st.write(
            f"""
            <div style="text-align: justify;">
                {TEXT_SETOR}
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
                    '<strong>Tabela</strong> - Distribuição de financiamentos externos da Carteira Ativa da Cofiex entre setores</p>',
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

                st.dataframe(S_TAB)

        
        with tab2:

            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])


            with col2:
                st.markdown(
                    '<strong>Gráfico</strong> - Distribuição de financiamentos externos da Carteira Ativa da Cofiex entre setores</p>',
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

                fig = setores_chart(filtered_df, distinct_df)
                st.plotly_chart(fig, use_container_width=True)