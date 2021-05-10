# -*- coding: utf-8 -*-
from datetime import datetime

import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
from pandas.core.dtypes.common import is_bool_dtype
from pandas.core.indexes.base import ensure_index_from_sequences
import plotly.express as px
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
from numpy import column_stack
from pandas.api.types import (is_datetime64_any_dtype, is_float_dtype,
                              is_integer_dtype, is_numeric_dtype,
                              is_object_dtype, is_string_dtype)

from core.components import (get_information_components, get_numeric_information_gui,
                             get_sample_df_data_children, get_string_information_gui, 
                             get_tab_filtering_components, get_table_dfcolumns,
                             container, row, col)
from core.data import (from_session, get_dt_colunas_data, modify_original_df,
                       parse_file_contents, to_session, value_as_type)
import plotly.graph_objects as go
import plotly.express as px

# CSS: http://getskeleton.com/
others=[
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    '/assets/custom.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'
]

app = dash.Dash(__name__, external_stylesheets=others)
# Important configuration to deal with non-created components
app.config['suppress_callback_exceptions']=True

def sample_data_skeleton():

    return dcc.Loading(
        id="loading-samples",
        type="graph",
        children=html.Div(
            id='sample-file-content',
            children=html.P("Click in 'Load data' button to load a dataset..."),
            style={
                "minHeight":"200px",
                "textAlign":"center",
                "paddingTop":"5px"
            }
        ),
    )

def columns_skeleton():
    return [
        html.Div([
            html.H4("Deal with the dataframe columns"),
            html.Div(className="row", children=[
                html.Div(className="one column", children=[""]),
                html.Div(className="eleven columns", children=[
                        dash_table.DataTable(
                            id="dt_colunas",
                            data=[],
                            editable=True,
                            columns=[
                                {'name': 'Column', 'id': 'coluna'},
                                {'name': 'Type', 'id': 'tipo'},
                                {'name': 'Rename to', 'type':'text', 'id': 'rename','editable':True, 'presentation':'input'},
                                {'name': 'Convert to', 'id': 'converter', 'editable':True, 'presentation':'dropdown'},
                                {'name': 'Remove?', 'id': 'excluir', 'editable':True, 'presentation':'dropdown'},
                                {'name': 'Fillna', 'id': 'fillna'},
                            ],
                            dropdown={
                                'excluir': {
                                    'clearable': False,
                                    'options': [
                                        {'label':'Keep column', 'value':False},
                                        {'label':'Remove column', 'value':True}
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
                    html.H3(["Original configuration"]),
                    html.Div(id="original_df_cols", children=[]),
                ]),
                html.Div(className="six columns", children=[
                    html.H3(["Result configuration"]),
                    html.Div(id="changed_df_cols", children=[]),
                ]),
            ])
        ])
    ]

app.layout = html.Div(id="container", children=[
    html.Div(className="row", children=[
        html.Div(className="nine columns", children=[
            html.H2(className="special-title",children=[html.I(className='fas fa-bars fa-rotate-90'), ' TARS']),
        ]),
        html.Div(className="three columns text-center", children=[
            dcc.Upload(
                id='upload-data',
                children=[
                    html.Button('Load data', className="button button-primary", title="CSV e Excel files only")
                ],
                style={
                    "textAlign": "center"
                },
                multiple=False
            ),
        ])
    ]),
    dcc.Store(id='store_original_df', storage_type='memory'),
    dcc.Store(id='store_modified_df', storage_type='memory'),
    dcc.Store(id='store_filters', storage_type='memory'),
    dcc.Tabs(id='tabs-main', value='tab-data', children=[
        dcc.Tab(label='Data', value='tab-data', children=sample_data_skeleton()),
        dcc.Tab(label='Columns', value='tab-columns', children=columns_skeleton()),
        dcc.Tab(label='Informations', value='tab-info', id="tab-info", children=get_information_components()),
        dcc.Tab(label='Filter data', value='tab-filter', id='tab-filter', children=get_tab_filtering_components()),
        dcc.Tab(label='Visualization', value='tag-visualizacao'),
    ])
])

@app.callback(Output('sample-file-content', 'children'),
            Input('store_original_df', 'data'),
            prevent_initial_call=True)
def show_sample_file_content(original_df_json):
    """Tab:Data, Section: Table with first rows
    """
    original_df = from_session(original_df_json)
    return get_sample_df_data_children(original_df)

@app.callback(Output('dt_colunas', 'data'),
            Input('store_original_df', 'data'),
            prevent_initial_call=True)
def show_columns_informations(original_df_json):
    """Tab:Colunas, Section: Deal with the dataframe columns
    """
    original_df = from_session(original_df_json)
    return get_dt_colunas_data(original_df)

@app.callback(Output('original_df_cols', 'children'),
            Input('store_original_df', 'data'),
            prevent_initial_call=True)
def show_original_columns(original_df_json):
    """Tab:Columns, Section: Original Configuration
    """
    original_df = from_session(original_df_json)
    columns_data = get_dt_colunas_data(original_df)
    return get_table_dfcolumns(columns_data, id='origin', df=original_df)

@app.callback(Output('tab-info', 'children'),
            Input('store_modified_df', 'data'),
            prevent_initial_call=True)
def show_information_gui(original_df_json):
    """Tab:Information, Section: Combobox of column
    """
    modified_df = from_session(original_df_json)
    return get_information_components(modified_df)

@app.callback(Output('tab-filter', 'children'),
            Input('store_modified_df', 'data'),
            prevent_initial_call=True)
def show_information_gui(original_df_json):
    """Tab:Information, Section: Combobox of column
    """
    modified_df = from_session(original_df_json)
    return get_tab_filtering_components(modified_df)

@app.callback(Output('data-table-filter', 'data'),
            Input('apply-filter-button', 'n_clicks'),
            State('data-table-filter', 'data'),
            State('inputfiltervalue', 'value'),
            State('dropdownoperador', 'value'),
            State('dropdowncolumns', 'value'),
            prevent_initial_call=True)
def apply_filter_button_click(n_clicks, filters_list, filter_value, filter_comp, filter_field):
    """Tab:Filter & Clean, Section: Button 'bolt'
    """
    if not filter_field or not filter_value or not filter_field.strip():
        raise PreventUpdate()

    filter_config = {'field': filter_field, 'comp': filter_comp, 'value': filter_value}
    
    if not filter_config in filters_list:
        filters_list.append(filter_config)

    return filters_list

@app.callback(
    Output('inputfiltervalue','disabled'), 
    Output('inputfiltervalue','value'), 
    Input('dropdownoperador','value'),
    State('inputfiltervalue','value'),
    )
def change_value_disabled(comparator_value, value_value):
    if comparator_value in ('isnull','notnull'):
        return (True, '')
    else:
        return (False, value_value)


@app.callback(Output('store_original_df','data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              prevent_initial_call=True,
              suppress_callback_exceptions=True)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        try:
            df = parse_file_contents(list_of_contents, list_of_names, list_of_dates) 
            return to_session(df)
        except Exception as e:
            raise PreventUpdate
    else:
        raise PreventUpdate

@app.callback(
    Output('store_modified_df','data'),
    Input('store_original_df', 'data'),
    Input('dt_colunas', 'data'))
def changed_cell_value(original_df_json, data):
    """Change the data of the Store for modified df
    """
    if not data:
        raise PreventUpdate

    original_df = from_session(original_df_json)
    modified_df = modify_original_df(original_df, data)
    return to_session(modified_df)

@app.callback(
    Output('changed_df_cols','children'),
    Input('store_modified_df','data'),
    Input('dt_colunas', 'data'))
def changed_cell_value(modified_df_json, data):
    """Show the modified columns in the Result configuration
    """
    if not data:
        raise PreventUpdate

    modified_df = from_session(modified_df_json)

    return get_table_dfcolumns(data, id='new', df=modified_df)

@app.callback(
    Output('information-content', 'children'),
    Input('store_modified_df', 'data'),
    Input('selected_column', 'value'),
    prevent_initial_call=True
)
def change_info_column_dropdown(df_json, info_column):
    """Show information when column dropdown, in Information tab is changed.
    """
    info_children = []
    
    if df_json and info_column != '-':
        df = from_session(df_json)
        
        dados = df[info_column]

        if is_numeric_dtype(dados):
            info_children = get_numeric_information_gui(dados, info_column)
        elif is_string_dtype(dados):
            info_children = get_string_information_gui(dados, info_column)
        #TODO: Mostrar mais tipos
        # elif is_bool_dtype(dados):
        #     info_children = get_bool_information_gui(dados, info_column)
        # elif is_datetime64_any_dtype(dados):
        #     info_children = get_datetime_information_gui(dados, info_column)
            
    return info_children


@app.callback(Output('data_filtering','data'),
              Input('data-table-filter', 'data'),
              State('store_modified_df', 'data'),
)
def update_output(filter_data, modified_df_json):
    
    df = pd.DataFrame()
    if modified_df_json:
        df = from_session(modified_df_json)

    if not df.empty and filter_data:
        
        for filter_row in filter_data:
            print(f"FILTRANDO: {filter_row['field']}->{filter_row['comp']}->{filter_row['value']}")
            typed_value = value_as_type(df, filter_row['field'], filter_row['value'])
            if filter_row['comp'] == 'eq':
                df = df[df[filter_row['field']] == typed_value]
            if filter_row['comp'] == 'ne':
                df = df[df[filter_row['field']] != typed_value]
            if filter_row['comp'] == 'gt':
                df = df[df[filter_row['field']] > typed_value]
            if filter_row['comp'] == 'ge':
                df = df[df[filter_row['field']] >= typed_value]
            if filter_row['comp'] == 'lt':
                df = df[df[filter_row['field']] < typed_value]
            if filter_row['comp'] == 'le':
                df = df[df[filter_row['field']] <= typed_value]

    return df.to_dict('records') if df is not None else []

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=False)
