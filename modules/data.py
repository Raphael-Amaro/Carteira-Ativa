import pandas as pd




# Filtragem de Dados – Carteira Ativa Cofiex
def carteira_ativa(df, tipoFinanciamento="Operação de Crédito Externo", fases=['Aprovada COFIEX', 'Em preparação', 'Aguardando negociação', 'Negociação agendada', 'Em negociação', 'Aguardando Assinatura', 'Em execução']):

    df = df.copy()
    
    filtered_df = df.query(
        'TipoFinanciamento == @tipoFinanciamento & deFase in @fases'
    )

    distinct_df = df.query(
        'TipoFinanciamento == @tipoFinanciamento & deFase in @fases'
    ).drop_duplicates('cdCartaConsulta')


    return filtered_df, distinct_df



# Filtragem de Dados – Totalidade das Autorizações no Período Estabelecido e mAbrangenciaNacional != "Federal
def sem_federal(df, tipoFinanciamento="Operação de Crédito Externo", fases=['Aprovada COFIEX', 'Em preparação', 'Aguardando negociação', 'Negociação agendada', 'Em negociação', 'Aguardando Assinatura', 'Em execução']):

    df = df.copy()

    
    filtered_df = df.query(
        'TipoFinanciamento == @tipoFinanciamento & deFase in @fases & nmAbrangenciaNacional != "Federal"'
    )

    distinct_df = df.query(
        'TipoFinanciamento == @tipoFinanciamento & deFase in @fases & nmAbrangenciaNacional != "Federal"'
    ).drop_duplicates('cdCartaConsulta')


    return filtered_df, distinct_df