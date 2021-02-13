"""Módulo que contém métodos auxiliares para construção da tela
"""
from datetime import datetime
from typing import List

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.exceptions import PreventUpdate


def parse_datacolumns(current_data: dict, id:str = "") -> List:
    table = dash_table.DataTable(
        id=f"t_cols_{id}",
        data=[
            {'name':'id','tipo':'int64'},
            {'name':'nome','tipo':datetime.now()},
        ],
        columns=[
            {'name': 'name', 'id': 'name'},
            {'name': 'tipo', 'id': 'tipo'},
        ]
    )
    return table

def get_sample_df_data_children(df):
    informations = [
        html.P([f"Total de colunas:{df.shape[1]}"]), 
        html.P([f"Total de linhas:{df.shape[0]}"]), 
    ]
    
    children = [
        dash_table.DataTable(
            id="data-table-01",
            data=df[:10].to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),
        html.Div(id="info-counts-01", children=informations)
    ]

    return children
