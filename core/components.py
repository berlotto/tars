"""Módulo que contém métodos auxiliares para construção da tela
"""
from datetime import datetime
from typing import List, Any

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.exceptions import PreventUpdate


def get_table_dfcolumns(current_data: dict, id:str, df: pd.DataFrame) -> List:
    table_data = []
    # {'coluna': 'id', 'tipo': 'int64', 'excluir': False, 'rename': 'nome', 'converter': 'int64', 'fillna': 'mean'}
    for col in current_data:
        if not col.get('excluir',False):
            _colname = col.get('coluna') \
                if not col.get('rename', False) \
                else col.get('rename')
            coldata = {
                'index': df.columns.get_loc(_colname),
                'nome' : _colname,
                'tipo' : col.get('tipo') if not col.get('converter', False) else col.get('converter'),
                'naonulos': df[_colname].notnull().count()
            }
            table_data.append(coldata)
    table = dash_table.DataTable(
        id=f"t_cols_{id}",
        data=table_data,
        columns=[
            {'name': '#', 'id': 'index'},
            {'name': 'Nome', 'id': 'nome'},
            {'name': 'Tipo', 'id': 'tipo'},
            {'name': 'Não nulos', 'id': 'naonulos'},
        ]
    )
    return table

def get_sample_df_data_children(df):
    informations = [
        html.Div(className="row", children=[
            html.Div(className="three columns", children=[
                html.H4([f"Total de colunas:{df.shape[1]}"]), 
            ]),
            html.Div(className="three columns", children=[
                html.H4([f"Total de linhas:{df.shape[0]}"]), 
            ]),
        ])
    ]
    
    children = [
        html.Div(id="info-counts-01", children=informations),
        dash_table.DataTable(
            id="data-table-01",
            data=df[:10].to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),
    ]

    return children


def container(children):
    return html.Div(className="container", children=children)


def row(children):
    return html.Div(className="row", children=children)


def col(classname, children):
    return html.Div(className=classname, children=children)


def get_information_components(df: pd.DataFrame) -> List[Any]:
    if df is None or df.empty:
        columns = ['-']
        col_options = [{'label':'-- falta selecionar os dados --', 'value':'-'}]
    else:
        columns = df.columns.to_list()
        col_options = [ {'label':c, 'value':c} for c in columns]
    children = [\
        row(
            col("six columns",[
                html.Label(htmlFor="selected_column",children="Selecione a coluna"),
                dcc.Dropdown(
                    id='selected_column',
                    options=col_options,
                    value=columns[0]
                ),
            ])
        ),
        row(col("twelve columns", children=[
            dcc.Loading(
                id="loading-information-content",
                type="graph",
                children=html.Div(id='information-content')
            )
        ]))
    ]

    return children