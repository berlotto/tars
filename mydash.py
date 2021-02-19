# -*- coding: utf-8 -*-
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from numpy import column_stack
from pandas.api.types import (is_datetime64_any_dtype, is_float_dtype,
                              is_integer_dtype, is_numeric_dtype,
                              is_object_dtype, is_string_dtype)

from core.components import (get_information_components,
                             get_sample_df_data_children, get_table_dfcolumns,
                             container, row, col)
from core.data import (from_session, get_dt_colunas_data, modify_original_df,
                       parse_file_contents, to_session)
import plotly.graph_objects as go
import plotly.express as px

# CSS: http://getskeleton.com/
others=[
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    '/assets/custom.css',
]

app = dash.Dash(__name__, external_stylesheets=others)

tabdata = [
    dcc.Loading(
        id="loading-samples",
        type="graph",
        children=html.Div(
            id='sample-file-content',
            children=[
                html.P("Clique em carregar dados...")
            ],
            style={
                "minHeight":"200px",
                "textAlign":"center",
                "paddingTop":"5px"
            }),
    ),
]

tabcolunas = [
    html.Div([
        html.H4("Tratamento de colunas do dataframe"),
        html.Div(className="row", children=[
            html.Div(className="one column", children=[""]),
            html.Div(className="eleven columns", children=[
                    dash_table.DataTable(
                        id="dt_colunas",
                        data=[],
                        editable=True,
                        columns=[
                            {'name': 'Coluna', 'id': 'coluna'},
                            {'name': 'Tipo', 'id': 'tipo'},
                            {'name': 'Novo nome', 'type':'text', 'id': 'rename','editable':True, 'presentation':'input'},
                            {'name': 'Converter', 'id': 'converter', 'editable':True, 'presentation':'dropdown'},
                            {'name': 'Excluir', 'id': 'excluir', 'editable':True, 'presentation':'dropdown'},
                            {'name': 'Fillna', 'id': 'fillna'},
                        ],
                        dropdown={
                            'excluir': {
                                'clearable': False,
                                'options': [
                                    {'label':'Não', 'value':False},
                                    {'label':'Sim', 'value':True}
                                ]
                            },
                            'converter': {
                                'clearable': True,
                                'options': [
                                    {'label':'object', 'value':'object'},
                                    {'label':'str', 'value':'str'},
                                    {'label':'bool', 'value':'bool'},
                                    {'label':'datetime64[ns]', 'value':'datetime64[ns]'},
                                    {'label':'int8', 'value':'int8'},
                                    {'label':'int16', 'value':'int16'},
                                    {'label':'int32', 'value':'int32'},
                                    {'label':'int64', 'value':'int64'},
                                    {'label':'uint8', 'value':'uint8'},
                                    {'label':'uint16', 'value':'uint16'},
                                    {'label':'uint32', 'value':'uint32'},
                                    {'label':'uint64', 'value':'uint64'},
                                    {'label':'float16', 'value':'float16'},
                                    {'label':'float32', 'value':'float32'},
                                    {'label':'float64', 'value':'float64'},
                                    {'label':'float128', 'value':'float128'},
                                ]
                            }
                        }
                    ),
            ]),
        ]),
        html.Div(className="row", children=[
            html.Div(className="one column", children=[""]),
            html.Div(className="five columns", children=[
                html.H3(["Configuração original"]),
                html.Div(id="original_df_cols", children=[]),
            ]),
            html.Div(className="six columns", children=[
                html.H3(["Configuração resultante"]),
                html.Div(id="changed_df_cols", children=[]),
            ]),
        ])
    ])
]

tabinfo = get_information_components(None),

app.layout = html.Div(id="container", 
children=[
    html.Div(className="row", children=[
        html.Div(className="nine columns", children=[
            html.H1(children='MyDash'),
        ]),
        html.Div(className="three columns", children=[
            dcc.Upload(
                id='upload-data',
                children=[
                    html.Button('Carregar dados', className="button button-primary"),
                    html.P("Arquivos CSV e Excel")
                ],
                style={
                    "textAlign": "center"
                },
                multiple=False
            ),
        ])
    ]),
    dcc.Store(id='original_df', storage_type='memory'),
    dcc.Store(id='df', storage_type='memory'),
    dcc.Tabs(id='tabs-example', value='tab-data', children=[
        dcc.Tab(label='Dados', value='tab-data', children=tabdata),
        dcc.Tab(label='Colunas', value='tab-colunas', children=tabcolunas),
        dcc.Tab(label='Informações', value='tab-info', 
                id="tab-info", children=tabinfo),
        dcc.Tab(label='Filtro e limpeza', value='tab-filtros'),
        dcc.Tab(label='Visualização', value='tag-visualizacao'),
    ]),
])


@app.callback(Output('original_df','data'),
              Output('dt_colunas', 'data'),
              Output('sample-file-content', 'children'),
              Output('original_df_cols','children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        df = parse_file_contents(list_of_contents, list_of_names, list_of_dates) 
        columns_data = get_dt_colunas_data(df)
        return (
            to_session(df), 
            columns_data, 
            get_sample_df_data_children(df),
            get_table_dfcolumns(columns_data, id='origin', df=df),
        )
    else:
        raise PreventUpdate


@app.callback(
    Output('df','data'),
    Output('changed_df_cols','children'),
    Output('tab-info','children'),
    Input('original_df', 'data'),
    Input('dt_colunas', 'data'))
def changed_cell_value(original_df_json, data):
    if not data:
        raise PreventUpdate

    original_df = from_session(original_df_json)
    
    modified_df = modify_original_df(original_df, data)
    t_novo = get_table_dfcolumns(data, id='novo', df=modified_df)
    tab_info_body = get_information_components(modified_df)

    return to_session(modified_df), [t_novo], tab_info_body


@app.callback(
    Output('information-content', 'children'),
    [Input('df', 'data'),
    Input('selected_column', 'value')]
)
def change_info_column_dropdown(df_json, info_column):
    
    info_children = []
    
    if df_json:
        df = from_session(df_json)
        
        dados = df[info_column]

        if is_numeric_dtype(dados):
            data_information = {
                'Minimo': dados.min(),
                'Máximo': dados.max(),
                'Quartil 25%': dados.quantile(q=0.25),
                'Média': dados.mean(),
                'Mediana': dados.median(),
                'Moda': dados.mode(),
                'Quartil 75%': dados.quantile(q=0.75),
                'Variância': dados.var(),
                'Desvio Padrão': dados.std(),
                'Vazios': dados.isna().sum(),
                'Quantidade': dados.count(),
                'Amplitude': dados.max() - dados.min(),
            }
            information_gui = dash_table.DataTable(
                id="data-info-numeric",
                data=[data_information],
                columns=[{'name': i, 'id': i} for i in data_information.keys()]
            )

            # Dados sem inf e na
            dados = dados[dados.isin([-np.inf, np.inf, np.NaN]) == False]

            fig = px.box(dados, y=info_column)
            graph = dcc.Graph(id="box-plot",figure=fig)

            figd =  px.histogram(dados, x=info_column, marginal="box", histnorm='probability')
            graphd = dcc.Graph(id="dist-plot",figure=figd)

            charts = row([
                col("six columns", children=[graph]),
                col("six columns", children=[graphd]),
            ])

            info_children = [information_gui, charts]

    return info_children


if __name__ == '__main__':
    app.run_server(debug=True)
