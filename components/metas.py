from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import dash_bootstrap_components as dbc
import pandas as pd
import dash
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar
from globals import *
from app import app

import pdb
from dash_bootstrap_templates import template_from_url, ThemeChangerAIO


# Carregando os dados do arquivo CSV
df_metas = pd.read_csv('df_metas.csv')



def renderizar_tabela_metas(df):
    rows = []
    for i, row in df.iterrows():
        remove_btn_id = f'btn-remover-meta-{i}'
        row_content = [
            html.Td(row['Nome']),
            html.Td(f'R$ {row["Valor"]:.2f}'),
            html.Td(f'R$ {row["Progresso"]:.2f}'),
            html.Td(row['Status']),
            html.Td(f'{row["Porcentagem"]}%'),
            html.Td(dbc.Button("Remover", id=remove_btn_id, color="danger", size="sm")),
        ]
        rows.append(html.Tr(row_content))

    table = dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Nome"), html.Th("Valor"),html.Th("Progresso"), html.Th("Status"), html.Th("Porcentagem"), html.Th()])),
            html.Tbody(rows),
        ],
        striped=True,
        bordered=True,
        hover=True,
    )

    return table

def criar_grafico_barras(df):
    fig = px.bar(df, x='Nome', y='Porcentagem', text='Porcentagem', color='Status',
                 labels={'Porcentagem': 'Progresso (%)', 'Nome': 'Meta', 'Progresso': 'Progresso'})
    fig.update_traces(texttemplate='%{text:.2s}%', textposition='auto', width=0.5)
    
    fig.update_layout(
        xaxis_title='Metas',
        yaxis_title='Progresso (%)',
        title='Progresso das Metas',

        xaxis=dict(
            showgrid=False,
            gridwidth=1,
        ),

        plot_bgcolor='rgba(0,0,0,0)',   # Define o fundo do plot como transparente
    )
    return dcc.Graph(figure=fig)



layout = dbc.Container([
    dbc.Row([
        dbc.Col([], width=0.5),  # Coluna vazia para criar espaço
        dbc.Col([
            html.Hr(),
            html.H4("Adicionar Nova Meta"),
            dbc.Input(id='input-nome-meta', type='text', placeholder='Nome', className="mb-2"),
            dbc.Input(id='input-valor-meta', type='number', placeholder='Valor necessário', className="mb-2"),
            dbc.Button("Adicionar Meta", id='btn-add-meta', color="primary", className="mt-2"),
        ], width=5),
        dbc.Col([], width=1),  # Coluna vazia para criar espaço
        dbc.Col([
            html.Hr(),
            html.H4("Incluir Valor Pago"),
            dbc.Select(
                id='select-meta-pagamento',
                options=[{'label': meta, 'value': meta} for meta in df_metas['Nome']],
                className="mb-2"
            ),
            dbc.Input(id='input-valor-pago', type='number', placeholder='Valor Pago', className="mb-2"),
            dbc.Button("Registrar Pagamento", id='btn-pagar-meta', color="success", className="mt-2"),
        ], width=5),
    ], className="mb-4"),  # Espaço após a primeira linha

    dbc.Row([
        dbc.Col([
            html.H2("Suas Metas"),
            html.Div(id='output-metas', children=[
                renderizar_tabela_metas(df_metas),
                criar_grafico_barras(df_metas)  # Adicionando o gráfico no output
            ]),
        ], width=12),
    ]),
])



def calcular_porcentagem(row):
    return round((row['Progresso'] / row['Valor']) * 100, 2)

df_metas['Porcentagem'] = df_metas.apply(calcular_porcentagem, axis=1)

def calcular_status(row):
    if row['Progresso'] >= row['Valor']:
        return 'Alcançado'
    elif row['Progresso'] > 0:
        return 'Juntando'
    else:
        return 'A juntar'

df_metas['Status'] = df_metas.apply(calcular_status, axis=1)

# O callback para atualizar as metas e o gráfico
@app.callback(
    Output('output-metas', 'children'),
    [
        Input('btn-add-meta', 'n_clicks'),
        Input('btn-pagar-meta', 'n_clicks'),
        *[Input(f'btn-remover-meta-{i}', 'n_clicks') for i in range(len(df_metas))]
    ],
    [
        State('input-nome-meta', 'value'),
        State('input-valor-meta', 'value'),
        State('select-meta-pagamento', 'value'),
        State('input-valor-pago', 'value')
    ]
)

def atualizar_metas_e_grafico(*args):
    global df_metas

    ctx = dash.callback_context
    triggered_component = ctx.triggered[0]['prop_id'].split('.')[0]

    output = []

    if triggered_component.startswith('btn-remover-meta'):
        index = int(triggered_component.split('-')[-1])
        df_metas = df_metas.drop(index)
        df_metas.reset_index(drop=True, inplace=True)
        df_metas.to_csv('df_metas.csv', index=False)
        output.append(renderizar_tabela_metas(df_metas))
    else:
        nome_meta, valor_meta, nome_meta_pago, valor_pago = args[-4:]

        if triggered_component == 'btn-add-meta' and nome_meta and valor_meta:
            new_row = pd.DataFrame([[nome_meta, valor_meta, 0, False, calcular_status({'Progresso': 0, 'Valor': valor_meta})]], columns=df_metas.columns)
            df_metas = pd.concat([df_metas, new_row], ignore_index=True)
            df_metas['Porcentagem'] = df_metas.apply(calcular_porcentagem, axis=1)
            df_metas.to_csv('df_metas.csv', index=False)
            output.append(renderizar_tabela_metas(df_metas))

        if triggered_component == 'btn-pagar-meta' and nome_meta_pago and valor_pago:
            meta_index = df_metas[df_metas['Nome'] == nome_meta_pago].index[0]
            df_metas.at[meta_index, 'Progresso'] += valor_pago
            df_metas.at[meta_index, 'Porcentagem'] = round((df_metas.at[meta_index, 'Progresso'] / df_metas.at[meta_index, 'Valor']) * 100, 2)
            df_metas['Status'] = df_metas.apply(calcular_status, axis=1)  
            df_metas.to_csv('df_metas.csv', index=False)
            output.append(renderizar_tabela_metas(df_metas))

    return [
        renderizar_tabela_metas(df_metas),
        criar_grafico_barras(df_metas)
    ]


layout_grafico = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafico-metas')
        ], width=12),
    ]),
])

