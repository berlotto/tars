"""Módulo que contém métodos auxiliares para construção da tela
"""
from datetime import datetime
from typing import Any, List

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
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
                html.H4([f"Number of columns:{df.shape[1]}"]), 
            ]),
            html.Div(className="three columns", children=[
                html.H4([f"Number of lines:{df.shape[0]}"]), 
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


def col(classname, children, **kwargs):
    return html.Div(className=classname, children=children, **kwargs)


def get_information_components(df: pd.DataFrame) -> List[Any]:
    if df is None or df.empty:
        columns = ['-']
        col_options = [{'label':'-- falta selecionar os dados --', 'value':'-'}]
    else:
        columns = df.columns.to_list()
        col_options = [ {'label':c, 'value':c} for c in columns]
    children = [
        row(col("six columns",[
                html.Label(htmlFor="selected_column",
                    children="Select the column to view your information"),
                dcc.Dropdown(
                    id='selected_column',
                    options=col_options,
                    value=columns[0]
                ),
        ])),
        row(col("twelve columns", children=[
            dcc.Loading(
                id="loading-information-content",
                type="graph",
                children=html.Div(id='information-content')
            )
        ]))
    ]

    return children

def panel(title, value):
    return html.Div(className="panel", children=[
        html.Div(title, className="panel-title"),
        html.P(str(value))
    ])


def get_numeric_information_gui(dados, info_column):
    numeric_totals_1 = \
        row([
            col("two columns", children=[panel('Minimum',dados.min())]),
            col("two columns", children=[panel('Quartile 25%', dados.quantile(q=0.25))]),
            col("two columns", children=[panel('Standar deviation', dados.std())]),
            col("two columns", children=[panel('Mean', dados.mean())]),
            col("two columns", children=[panel('Mode', dados.mode())]),
            col("two columns", children=[panel('Count total', dados.count())]),
        ])
    numeric_totals_2 = \
        row([
            col("two columns", children=[panel('Maximum', dados.max())]),
            col("two columns", children=[panel('Quartile 75%', dados.quantile(q=0.75))]),
            col("two columns", children=[panel('Variance', dados.var())]),
            col("two columns", children=[panel('Median', dados.median())]),
            col("two columns", children=[panel('Amplitude', dados.max() - dados.min())]),
            col("two columns", children=[panel('Count empty', dados.isna().sum())]),
        ])

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

    return [numeric_totals_1, numeric_totals_2, charts]

def get_string_information_gui(dados, info_column):
    components = []

    components.append(
        row([
            col("four columns", children=[panel("Count total", dados.count())]),
            col("four columns", children=[panel("Count unique", dados.nunique())]),
            col("four columns", children=[panel("Count empty",  dados.isna().sum())]),
        ])
    )

    # Gerar o df com a contagem de itens na serie de dados
    contagem = dados.value_counts()

    components.append(
        dcc.Graph(
            id='itens-pie',
            figure=px.bar(contagem)
        )
    )

    return components

def get_tab_filtering_components(df: pd.DataFrame = None) -> List:
    
    df_columns = df.columns if df is not None else []

    dataframe_columns=[
        {"name": i, "id": i, "selectable": True} for i in df_columns
    ]
    dataframe_data=df.to_dict('records') if df is not None else []

    dropdowncolumns_comp = dcc.Dropdown(
        id='dropdowncolumns',
        options=[
            {"label": i, "value": i} for i in df_columns
        ],
        value='',
        clearable=True
    )

    dropdownoperador_comp =  dcc.Dropdown(
        id='dropdownoperador',
        options=[
            {"label": "equal", "value": "eq"},
            {"label": "different", "value": "ne"},
            {"label": "greater then", "value": "gt"},
            {"label": "greater then or equal to", "value": "ge"},
            {"label": "less then", "value": "lt"},
            {"label": "less then or equal to", "value": "le"},
            {"label": "empty", "value": "isnull"},
            {"label": "between", "value": "between"},
            {"label": "one of this", "value": "in"},                
            {"label": "contains", "value": "contains"},                
        ],
        value='eq',
        clearable=False
    )
    inputfiltervalue_comp = dcc.Input(
        id="inputfiltervalue",
        type='text',
        debounce=True, # Change only on ENTER or LOST FOCUS
        placeholder="Input a value for the filter",
    )

    datafilters_components = [
        html.H5('Row filters'),
        row([
            col("six columns", children=[
                html.Label(htmlFor="dropdowncolumns",children="Select one column"),
                row([
                    col('six columns', children=[dropdowncolumns_comp]),
                    col('three columns', children=[dropdownoperador_comp]),
                    col('three columns', children=[inputfiltervalue_comp], id="inputfiltervalue_col"),
                ])
                ,
            ]),
            col('six columns', children=[
                html.P('Selected filters')
            ])
        ]),
        html.H5('Resultant data'),
    ]

    return [
        html.Div(children=[
            html.Div(children=datafilters_components),
            dash_table.DataTable(
                id="data_filtering",
                data=dataframe_data,
                columns=dataframe_columns,
                editable=False,
                row_deletable=False,
                sort_action='native',
                sort_mode="multi",
                filter_action='native',
                row_selectable='multi',
                page_action='native',
                page_size= 50,
            )
        ])
    ]