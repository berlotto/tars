# -*- coding: utf-8 -*-
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from numpy import column_stack

from core.components import get_sample_df_data_children, get_table_dfcolumns
from core.data import (from_session, get_dt_colunas_data, parse_file_contents,
                       to_session, modify_original_df)

# CSS: http://getskeleton.com/
others=['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=others)

tabdata = [
    dcc.Loading(
        id="loading-samples",
        type="graph",
        children=html.Div(id='sample-file-content',children=[""],style={"min-height":"200px"}),
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
                    html.Button('Carregar dados'),
                    html.P("Arquivos CSV e Excel")
                ],
                style={
                    "textAlign": "right"
                },
                multiple=False
            ),
        ])
    ]),
    dcc.Store(id='original_df', storage_type='session'),
    dcc.Store(id='df', storage_type='session'),
    dcc.Tabs(id='tabs-example', value='tab-data', children=[
        dcc.Tab(label='Dados', value='tab-data', children=tabdata),
        dcc.Tab(label='Colunas', value='tab-colunas', children=tabcolunas),
        dcc.Tab(label='Informações', value='tab-info'),
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
            get_table_dfcolumns(columns_data, id='origin', df=df)
        )
    else:
        raise PreventUpdate


@app.callback(
    Output('df','data'),
    Output('changed_df_cols','children'),
    Input('original_df', 'data'),
    Input('dt_colunas', 'data'))
def changed_cell_value(original_df_json, data):
    if not data:
        raise PreventUpdate

    original_df = from_session(original_df_json)
    
    modified_df = modify_original_df(original_df, data)
    t_novo = get_table_dfcolumns(data, id='novo', df=modified_df)

    return to_session(modified_df), [t_novo]


if __name__ == '__main__':
    app.run_server(debug=True)
