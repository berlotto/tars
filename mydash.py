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

from core.components import get_sample_df_data_children, parse_datacolumns
from core.data import (from_session, get_dt_colunas_data, parse_file_contents,
                       to_session)

# CSS: http://getskeleton.com/
others=['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=others)

tabdata = [
        dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Solte aqui seu CSV ou clique aqui para selecionar'
        ]),
        style={
            'width': '99%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='sample-file-content'),
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
                                {'label':'int32', 'value':'int32'},
                                {'label':'int64', 'value':'int64'},
                                {'label':'bool', 'value':'bool'},
                                {'label':'float64', 'value':'float64'},
                                {'label':'datetime64[ns]', 'value':'datetime64[ns]'}
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
                html.H3(["Nova configuração"]),
                html.Div(id="changed_df_cols", children=[]),
            ]),
        ])
    ])
]


app.layout = html.Div(id="container", 
children=[
    html.H1(children='MyDash'),
    dcc.Store(id='original_df', storage_type='session'),
    dcc.Store(id='df', storage_type='session'),
    dcc.Tabs(id='tabs-example', value='tab-data', children=[
        dcc.Tab(label='Dados', value='tab-data', children=tabdata),
        dcc.Tab(label='Colunas', value='tab-colunas', children=tabcolunas),
        dcc.Tab(label='Informações', value='tab-info'),
        dcc.Tab(label='Filtro e limpeza', value='tab-filtros'),
        dcc.Tab(label='Vizualização', value='tag-visualizacao'),
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
            parse_datacolumns(columns_data, id='origin')
        )
    else:
        raise PreventUpdate


@app.callback(
    Output('df','data'),
    Output('changed_df_cols','children'),
    Input('original_df', 'data'),
    Input('dt_colunas', 'data'))
def changed_cell_value(original_df_json, data):
    original_df = from_session(original_df_json)
    t_novo = parse_datacolumns(data, id='novo')

    return original_df.to_json(), [t_novo]


if __name__ == '__main__':
    app.run_server(debug=True)
