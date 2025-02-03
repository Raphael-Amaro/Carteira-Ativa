import pandas as pd
import numpy as np
import locale
import os
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
from modules.conf import brazil_vlr, subtractM, decimais_vlr, brazil_per, decimais_per, subtractB, colors_list
import streamlit as st
import plotly.graph_objects as go

import geobr  # para ler o shape do Brasil
import json
import plotly.express as px
import geopandas as gpd


# GRÁFICO


def uf_chart_interativo(filtered_df_sem_federal):
    """
    Retorna (df_merged, fig):
      - df_merged: o geodataframe com a coluna "Contagem" já mergeada.
      - fig: figura Plotly interativa com o mapa coroplético usando custom_data + hovertemplate
    """

    # Caminho do arquivo GeoJSON
    json_path = "data/br_uf.geojson"

    # Garantir que o diretório "data" existe antes de tentar ler/escrever
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    # Verifica se o arquivo existe antes de tentar ler
    if os.path.exists(json_path):
        try:
            br_uf = gpd.read_file(json_path)  # Tenta carregar o arquivo salvo
            print("Arquivo carregado com sucesso!")
        except Exception as e:
            print(f"Erro ao ler o arquivo: {e}")
            print("Baixando os dados novamente...")
            br_uf = geobr.read_state()  # Baixa os dados
            br_uf.to_file(json_path, driver="GeoJSON")  # Salva corretamente
    else:
        print("Arquivo não encontrado. Baixando os dados...")
        br_uf = geobr.read_state()  # Baixa os dados
        br_uf.to_file(json_path, driver="GeoJSON")  # Salva corretamente


    # 2) Agrupa e soma o 'VlDolar' por UF
    df_uf_ano_end = (
        filtered_df_sem_federal
        .groupby(['cdUF_IBGE'])['VlDolar']
        .sum()
        .reset_index()
        .rename(columns={"cdUF_IBGE": "code_state", "VlDolar": "Contagem"})
    )

    # 3) Determina o valor máximo para configurar a escala de cores
    overall_max = df_uf_ano_end['Contagem'].max()

    # 4) Faz o merge do shape com o DataFrame
    df_merged = pd.merge(
        br_uf,
        df_uf_ano_end,     
        on='code_state',
        how='left'
    )

    # Preenche valores NaN com 0
    df_merged['Contagem'] = df_merged['Contagem'].fillna(0)

    # 5) Cria uma coluna formatada para exibir no hover
    #    Ex: "1,3" => "1,3" (depois mostraremos o "B" no hovertemplate)
    df_merged['ValorFormatado'] = df_merged['Contagem'].apply(
        lambda x: brazil_vlr(x / subtractB, decimais_vlr)
    )

    # 6) Converte o geodataframe em GeoJSON
    df_merged_json = json.loads(df_merged.to_json())

    # 7) Definimos min, mid, max para a cor
    min_value = 0
    max_value = overall_max if overall_max > 0 else 0
    mid_value = (min_value + max_value) / 2

    # 8) Cria o mapa coroplético interativo
    #    - O parâmetro 'custom_data' recebe a coluna formatada
    #    - Não precisamos mais exibir "Contagem" no hover_data
    fig = px.choropleth_mapbox(
        df_merged,
        geojson=df_merged_json,
        locations='code_state',
        featureidkey='properties.code_state',
        color='Contagem',
        color_continuous_scale=["#ffffff", "#1D3C69"],
        range_color=(min_value, max_value),
        mapbox_style="white-bg",#"carto-positron",
        zoom=2.8,
        center={"lat": -14.2, "lon": -51.9},
        opacity=0.8,
        hover_name='abbrev_state',   # mostrará a sigla do estado
        hover_data={
            "code_state": False      # oculta a coluna code_state no hover
        },
        custom_data=["ValorFormatado"]  # envia nossa coluna formatada para o hovertemplate
    )

    # 9) Personaliza o texto de hover com hovertemplate
    #    %{hovertext} = valor definido em hover_name (sigla do estado)
    #    %{customdata[0]} = 'ValorFormatado'
    fig.update_traces(
        hovertemplate=(
            "Estado: %{hovertext}<br>"
            "Valor: %{customdata[0]}B<extra></extra>"
        )
    )

    # 10) Customiza a cor e o rótulo do eixo de cores (Colorbar)
    fig.update_layout(
        margin=dict(r=0, l=0, t=0, b=0),  # Tira margens extras
        coloraxis_colorbar=dict(
            title="(US$)",
            ticks="outside",
            tickvals=[min_value, mid_value, max_value],
            ticktext=[
                f"{brazil_vlr(min_value/subtractB, decimais_vlr)}B",
                f"{brazil_vlr(mid_value/subtractB, decimais_vlr)}B",
                f"{brazil_vlr(max_value/subtractB, decimais_vlr)}B"
            ]
        )
    )

    return df_merged, fig






# Texto: Distribuição de financiamentos externos autorizados entre unidades federativas, conforme a data de autorização
def text_uf(data_text_end_y):




    # Remove as linhas onde a coluna 'Contagem' tem valores NaN
    data_text_end_y = data_text_end_y.dropna(subset=['Contagem'])

    # Eliminar as linhas onde 'Contagem' é igual a 0
    data_text_end_y = data_text_end_y.query('Contagem != 0')

    # Seleciona as colunas desejadas e renomeia 'Contagem' para 'end_y'
    data_text_end_y = data_text_end_y[['abbrev_state', 'name_state', 'name_region', 'Contagem']].rename(columns={'Contagem': 'end_y'}).sort_values(by='end_y', ascending=False)

    RS = (
        "Esse elevado montante direcionado ao Estado decorre diretamente da publicação da Resolução Cofiex nº 26, de 6 de junho de 2024, a qual priorizou a aprovação de financiamentos externos destinados ao enfrentamento das consequências dos eventos climáticos que resultaram na declaração de estado de calamidade pública na região. "
    )

    lista_uf_texto = []
    # for sem região
    for i in range(len(data_text_end_y)):
        percentual = brazil_per((data_text_end_y.iloc[i]['end_y'] / data_text_end_y['end_y'].sum()) * 100, decimais_per)
        if i == 0:
            lista_uf_texto.append(f"com especial destaque para o Estado de {data_text_end_y.iloc[i]['name_state']} ({data_text_end_y.iloc[i]['abbrev_state']}), pertencente à região {data_text_end_y.iloc[i]['name_region']}, que registrou o maior volume recebido, alcançando a expressiva cifra de US$ {brazil_vlr( data_text_end_y.iloc[i]['end_y'] / subtractB, decimais_vlr)} {'bilhões' if (data_text_end_y.iloc[i]['end_y'] / subtractB) >= 2 else 'bilhão' }, correspondendo a {percentual} do total financeiro. { RS if str(data_text_end_y.iloc[i]['name_state']) == 'Rio Grande Do Sul' else ''}")#As unidades federativas ordenadas pelo volume financeiro autorizado são as seguintes: ")
            
        elif i == len(data_text_end_y) - 1:
            None
            # lista_uf_texto.append(f"e {data_text_end_y.iloc[i]['name_state']} ({data_text_end_y.iloc[i]['abbrev_state']}), com US$ {brazil_vlr( data_text_end_y.iloc[i]['end_y'] / subtractB, decimais_vlr)} {'bilhões' if (data_text_end_y.iloc[i]['end_y'] / subtractB) >= 2 else 'bilhão' } ({percentual}).")
        else:
            None
            # lista_uf_texto.append(f"{data_text_end_y.iloc[i]['name_state']} ({data_text_end_y.iloc[i]['abbrev_state']}), com US$ {brazil_vlr( data_text_end_y.iloc[i]['end_y'] / subtractB, decimais_vlr)} {'bilhões' if (data_text_end_y.iloc[i]['end_y'] / subtractB) >= 2 else 'bilhão' } ({percentual}); ")

    # Une todos os elementos da lista_uf_texto em uma única string 
    uf_end_y_texto = ''.join(lista_uf_texto)

    return (
        f"O gráfico e a tabela apresentados a seguir demonstram a distribuição dos financiamentos externos da Carteira Ativa da Cofiex entre as unidades federativas do Brasil, excluindo-se os de abrangência federal. "
        
        f"Constata-se que a concentração de recursos foi significativamente mais acentuada em algumas unidades federativas, "
        f"{uf_end_y_texto}"
        
    )






## Tabela e Texto: Distribuição da Carteira Ativa de acordo com a fase de andamento dos projetos 
def uf_table(filtered_df_sem_federal, distinct_df_sem_federal, data_text_end_y):

    # Criar um dicionário de mapeamento de 'cdUF_IBGE' para 'name_state'
    state_mapping = data_text_end_y.set_index('code_state')['name_state'].to_dict()

    # Continuar com o cálculo
    carteira_tab = pd.DataFrame({
        'Número de Projetos': distinct_df_sem_federal.groupby('cdUF_IBGE')['cdCartaConsulta'].count(), 
        'Valor de Empréstimo': filtered_df_sem_federal.groupby('cdUF_IBGE')['VlDolar'].sum(),
        'Valor de Contrapartida': filtered_df_sem_federal.groupby('cdUF_IBGE')['CpVlDolar'].sum()
    })
    carteira_tab.fillna(0, inplace=True)

    # Aplicar o cálculo do percentual formatado
    carteira_tab['Empréstimo / Total (%)'] = (
        carteira_tab['Valor de Empréstimo'] / carteira_tab['Valor de Empréstimo'].sum()
    )

    # Remover as fases com valor zero em 'Valor de Empréstimo'
    carteira_tab = carteira_tab[carteira_tab['Valor de Empréstimo'] > 0]

    carteira_tab.sort_values(by='Valor de Empréstimo', ascending=False, inplace=True)

    # Substituir o índice do dataframe 'carteira_tab' usando o mapeamento
    carteira_tab.index = carteira_tab.index.map(state_mapping)


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
    carteira_tab.index.name = 'Unidade Federativa'

    

    

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

    

    return (
        f"Explorando os aspectos geográficos dos projetos e programas da Carteira Ativa da Cofiex, a tabela subsequente ilustra a distribuição dos financiamentos externos entre as diversas regiões do país. ",
        carteira_tab_str,
        brazil_vlr(carteira_tab['Número de Projetos'].sum(), 0),
        brazil_vlr(carteira_tab['Valor de Empréstimo'].sum() / subtractM, decimais_vlr),
        brazil_vlr(carteira_tab['Valor de Contrapartida'].sum() / subtractM, decimais_vlr)
    )












def uf(filtered_df_sem_federal, distinct_df_sem_federal):
    st.header("Regiões", divider='gray')

    if 'TEXT_UF' in locals():
        pass  # Ou outra ação
    else:
        data_text_end_y, fig = uf_chart_interativo(filtered_df_sem_federal)
        _, U_TAB, u_tab_0sum, u_tab_1sum, u_tab_2sum = uf_table(filtered_df_sem_federal, distinct_df_sem_federal, data_text_end_y)
        TEXT_UF = text_uf(data_text_end_y)
    
    with st.container():

        st.write(
            f"""
            <div style="text-align: justify;">
                {TEXT_UF}
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
                    '<strong>Tabela</strong> - Distribuição de financiamentos externos da Carteira Ativa da Cofiex entre unidades federativas</p>',
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

                st.dataframe(U_TAB)

        
        with tab2:

            col1, col2, col3 = st.columns([0.3, 0.4, 0.3])


            with col2:
                st.markdown(
                    '<strong>Gráfico</strong> - Distribuição de financiamentos externos da Carteira Ativa da Cofiex entre unidades federativas</p>',
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

                df_merged, fig = uf_chart_interativo(filtered_df_sem_federal)
                st.plotly_chart(fig, use_container_width=True)