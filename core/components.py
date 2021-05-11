"""Módulo que contém métodos auxiliares para construção da tela
"""
from typing import Any, List

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
import plotly.express as px
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype


def get_type_count(df, type_name):
    types_of_columns = [
        (
            c,
            "number"
            if is_numeric_dtype(df[c])
            else "date"
            if is_datetime64_any_dtype(df[c])
            else "string",
        )
        for c in df.columns
    ]
    dff = pd.DataFrame(types_of_columns, columns=["column", "type_name"])
    counts = dff.type_name.value_counts()
    try:
        return counts[type_name]
    except KeyError:
        return 0


def get_df_used_memory(df):
    in_kb = in_mb = in_gb = 0
    in_bytes = sum([size for size in df.memory_usage(deep=True)])
    total_size = f"{in_bytes} B"
    if in_bytes > 1_000:
        in_kb = round(in_bytes / 1_000, 2)
        total_size = f"{in_kb} KB"
    if in_kb > 1_000:
        in_mb = round(in_kb / 1_000, 2)
        total_size = f"{in_mb} MB"
    if in_mb > 1_000:
        in_gb = round(in_mb / 1_000, 2)
        total_size = f"{in_gb} MB"
    return total_size


def get_table_dfcolumns(current_data: dict, id: str, df: pd.DataFrame) -> List:
    table_data = []
    # {'coluna': 'id', 'tipo': 'int64', 'excluir': False, 'rename': 'nome', 'converter': 'int64', 'fillna': 'mean'}
    for col in current_data:
        if not col.get("excluir", False):
            _colname = (
                col.get("coluna") if not col.get("rename", False) else col.get("rename")
            )
            coldata = {
                "index": df.columns.get_loc(_colname),
                "nome": _colname,
                "tipo": col.get("tipo")
                if not col.get("converter", False)
                else col.get("converter"),
                "naonulos": df[_colname].notnull().count(),
            }
            table_data.append(coldata)
    table = dash_table.DataTable(
        id=f"t_cols_{id}",
        data=table_data,
        columns=[
            {"name": "#", "id": "index"},
            {"name": "Nome", "id": "nome"},
            {"name": "Tipo", "id": "tipo"},
            {"name": "Não nulos", "id": "naonulos"},
        ],
    )
    return table


def get_sample_df_data_children(df):
    informations = [
        html.Div(
            className="row",
            children=[
                html.Table(
                    className="twelve columns infotable",
                    children=[
                        html.Tr(
                            [
                                html.Th(["Rows :"]),
                                html.Td([f"{df.shape[0]}"]),
                                html.Th(["Features :"]),
                                html.Td([f"{df.shape[1]}"]),
                                html.Th(["Duplicates :"]),
                                html.Td(
                                    [df.duplicated(subset=None, keep="first").sum()]
                                ),
                                html.Th(["Categorical :"]),
                                html.Td([get_type_count(df, "string")]),
                                html.Th(["Numerical :"]),
                                html.Td([get_type_count(df, "number")]),
                                html.Th(["Date :"]),
                                html.Td([get_type_count(df, "date")]),
                                html.Th(["Used memory :"]),
                                html.Td([f"{get_df_used_memory(df)}"]),
                            ]
                        ),
                    ],
                ),
            ],
        ),
        html.H4("First lines of data"),
    ]

    children = [
        html.Div(id="info-counts-01", children=informations),
        dash_table.DataTable(
            id="data-table-01",
            data=df[:25].to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
        ),
    ]

    return children


def container(children):
    return html.Div(className="container", children=children)


def row(children):
    return html.Div(className="row", children=children)


def col(classname, children, **kwargs):
    return html.Div(className=classname, children=children, **kwargs)


def get_information_components(df: pd.DataFrame = None) -> List[Any]:
    if df is None or df.empty:
        columns = ["-"]
        col_options = [{"label": "-- falta selecionar os dados --", "value": "-"}]
    else:
        columns = df.columns.to_list()
        col_options = [{"label": c, "value": c} for c in columns]
    children = [
        row(
            col(
                "six columns",
                [
                    html.Label(
                        htmlFor="selected_column",
                        children="Select the column to view your information",
                    ),
                    dcc.Dropdown(
                        id="selected_column", options=col_options, value=columns[0]
                    ),
                ],
            )
        ),
        row(
            col(
                "twelve columns",
                children=[
                    dcc.Loading(
                        id="loading-information-content",
                        type="graph",
                        children=html.Div(id="information-content"),
                    )
                ],
            )
        ),
    ]

    return children


def panel(title, value):
    return html.Div(
        className="panel",
        children=[html.Div(title, className="panel-title"), html.P(str(value))],
    )


def get_numeric_information_gui(dados, info_column):

    mode = ",".join([str(x) for x in dados.mode()])

    numeric_totals_1 = row(
        [
            col("two columns", children=[panel("Minimum", dados.min())]),
            col("two columns", children=[panel("Q1 (25%)", dados.quantile(q=0.25))]),
            col("two columns", children=[panel("Mean", dados.mean())]),
            col("two columns", children=[panel("Median", dados.median())]),
            col("two columns", children=[panel("Q3 (75%)", dados.quantile(q=0.75))]),
            col("two columns", children=[panel("Maximum", dados.max())]),
        ]
    )
    numeric_totals_2 = row(
        [
            col("two columns", children=[panel("Standar deviation", dados.std())]),
            col("two columns", children=[panel("Mode", mode)]),
            col("two columns", children=[panel("Variance", dados.var())]),
            col(
                "two columns", children=[panel("Amplitude", dados.max() - dados.min())]
            ),
            col("two columns", children=[panel("Count total", dados.count())]),
            col("two columns", children=[panel("Count empty", dados.isna().sum())]),
        ]
    )

    # Dados sem inf e na
    dados = dados[dados.isin([-np.inf, np.inf, np.NaN]) == False]  # noqa: E712

    fig = px.box(dados, y=info_column)
    graph = dcc.Graph(id="box-plot", figure=fig)

    figd = px.histogram(dados, x=info_column, marginal="box", histnorm="probability")
    graphd = dcc.Graph(id="dist-plot", figure=figd)

    charts = row(
        [
            col("six columns", children=[graph]),
            col("six columns", children=[graphd]),
        ]
    )

    return [numeric_totals_1, numeric_totals_2, charts]


def get_string_information_gui(dados, info_column):
    components = []

    components.append(
        row(
            [
                col("four columns", children=[panel("Count total", dados.count())]),
                col("four columns", children=[panel("Count unique", dados.nunique())]),
                col(
                    "four columns", children=[panel("Count empty", dados.isna().sum())]
                ),
            ]
        )
    )

    # Gerar o df com a contagem de itens na serie de dados
    contagem = dados.value_counts()

    def get_unique_values(s):
        return [html.Tr(html.Td([x])) for x in s.unique()]

    components.append(
        row(
            [
                col(
                    "twelve columns",
                    [
                        dcc.Graph(id="itens-pie", figure=px.bar(contagem)),
                    ],
                )
            ]
        )
    )

    return components


def get_tab_filtering_components(df: pd.DataFrame = None) -> List:

    df_columns = []
    dataframe_data = []

    if df is not None:
        df_columns = df.columns

        dataframe_columns = [
            {"name": i, "id": i, "selectable": True} for i in df_columns
        ]
        dataframe_data = df.to_dict("records")

    columns_options = [{"label": i, "value": i} for i in df_columns]

    dropdowncolumns_comp = dcc.Dropdown(
        id="dropdowncolumns", options=columns_options, value="", clearable=True
    )

    operator_options = [
        {"label": "equal (=)", "value": "eq"},
        {"label": "different (!=)", "value": "ne"},
        {"label": "greater then (>)", "value": "gt"},
        {"label": "greater then or equal to (>=)", "value": "ge"},
        {"label": "less then (<)", "value": "lt"},
        {"label": "less then or equal to (<=)", "value": "le"},
        {"label": "one of this", "value": "in"},
        {"label": "contains", "value": "contains"},
        {"label": "is empty", "value": "isnull"},
        {"label": "is not empty", "value": "notnull"},
        {"label": "between", "value": "between"},
    ]

    dropdownoperador_comp = dcc.Dropdown(
        id="dropdownoperador", options=operator_options, value="eq", clearable=False
    )
    inputfiltervalue_comp = dcc.Input(
        id="inputfiltervalue",
        type="text",
        debounce=True,  # Change only on ENTER or LOST FOCUS
        placeholder="Input a value for the filter",
        disabled=False,
    )

    datafilters_components = [
        html.H5("Row filters"),
        row(
            [
                col(
                    "six columns",
                    children=[
                        html.Label(
                            htmlFor="dropdowncolumns", children="Select one column"
                        ),
                        row(
                            [
                                col("four columns", children=[dropdowncolumns_comp]),
                                col("three columns", children=[dropdownoperador_comp]),
                                col(
                                    "four columns",
                                    children=[inputfiltervalue_comp],
                                    id="inputfiltervalue_col",
                                ),
                                col(
                                    "one column",
                                    children=[
                                        html.Button(
                                            id="apply-filter-button",
                                            n_clicks=0,
                                            style={"padding-top": "4px"},
                                            children=[
                                                html.I(className="fas fa-2x fa-bolt")
                                            ],
                                        ),
                                    ],
                                ),
                            ]
                        ),
                    ],
                ),
                col(
                    "six columns",
                    children=[
                        dash_table.DataTable(
                            id="data-table-filter",
                            columns=[
                                {"name": "Field ", "id": "field"},
                                {"name": "Operator ", "id": "comp"},
                                {"name": "Value", "id": "value"},
                            ],
                            data=[],
                            editable=False,
                            row_deletable=True,
                        ),
                    ],
                ),
            ]
        ),
        html.H5("Resultant data"),
    ]

    table = None
    if dataframe_data and dataframe_columns:
        table = dash_table.DataTable(
            id="modified_filtered_table",
            data=dataframe_data,
            columns=dataframe_columns,
            editable=False,
            row_deletable=False,
            sort_action="native",
            sort_mode="multi",
            page_action="native",
            page_size=50,
        )
    else:
        table = dash_table.DataTable(
            id="modified_filtered_table",
            data=[],
            columns=[],
            editable=False,
            row_deletable=False,
            sort_action="native",
            sort_mode="multi",
            page_action="native",
            page_size=50,
        )

    return [html.Div(children=[html.Div(children=datafilters_components), table])]


def get_data_tab_components():

    return dcc.Loading(
        id="loading-samples",
        type="graph",
        children=html.Div(
            id="sample-file-content",
            children=html.P("Click in 'Load data' button to load a dataset..."),
            style={"minHeight": "200px", "textAlign": "center", "paddingTop": "5px"},
        ),
    )


def get_columns_tab_components():
    return [
        html.Div(
            [
                html.H4("Deal with the dataframe columns"),
                html.Div(
                    className="row",
                    children=[
                        html.Div(className="one column", children=[""]),
                        html.Div(
                            className="eleven columns",
                            children=[
                                dash_table.DataTable(
                                    id="dt_colunas",
                                    data=[],
                                    editable=True,
                                    columns=[
                                        {"name": "Column", "id": "coluna"},
                                        {"name": "Type", "id": "tipo"},
                                        {
                                            "name": "Rename to",
                                            "type": "text",
                                            "id": "rename",
                                            "editable": True,
                                            "presentation": "input",
                                        },
                                        {
                                            "name": "Convert to",
                                            "id": "converter",
                                            "editable": True,
                                            "presentation": "dropdown",
                                        },
                                        {
                                            "name": "Remove?",
                                            "id": "excluir",
                                            "editable": True,
                                            "presentation": "dropdown",
                                        },
                                        {"name": "Fillna", "id": "fillna"},
                                    ],
                                    dropdown={
                                        "excluir": {
                                            "clearable": False,
                                            "options": [
                                                {
                                                    "label": "Keep column",
                                                    "value": False,
                                                },
                                                {
                                                    "label": "Remove column",
                                                    "value": True,
                                                },
                                            ],
                                        },
                                        "converter": {
                                            "clearable": True,
                                            "options": [
                                                {"label": "object", "value": "object"},
                                                {"label": "str", "value": "str"},
                                                {"label": "bool", "value": "bool"},
                                                {
                                                    "label": "datetime64[ns]",
                                                    "value": "datetime64[ns]",
                                                },
                                                {"label": "int8", "value": "int8"},
                                                {"label": "int16", "value": "int16"},
                                                {"label": "int32", "value": "int32"},
                                                {"label": "int64", "value": "int64"},
                                                {"label": "uint8", "value": "uint8"},
                                                {"label": "uint16", "value": "uint16"},
                                                {"label": "uint32", "value": "uint32"},
                                                {"label": "uint64", "value": "uint64"},
                                                {
                                                    "label": "float16",
                                                    "value": "float16",
                                                },
                                                {
                                                    "label": "float32",
                                                    "value": "float32",
                                                },
                                                {
                                                    "label": "float64",
                                                    "value": "float64",
                                                },
                                                {
                                                    "label": "float128",
                                                    "value": "float128",
                                                },
                                            ],
                                        },
                                    },
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="row",
                    children=[
                        html.Div(className="one column", children=[""]),
                        html.Div(
                            className="five columns",
                            children=[
                                html.H3(["Original configuration"]),
                                html.Div(id="original_df_cols", children=[]),
                            ],
                        ),
                        html.Div(
                            className="six columns",
                            children=[
                                html.H3(["Result configuration"]),
                                html.Div(id="changed_df_cols", children=[]),
                            ],
                        ),
                    ],
                ),
            ]
        )
    ]


def get_vis_tab_components():

    grap_type_options = [
        {"label": "Line chart", "value": "line"},
        {"label": "Vertical Bar chart", "value": "vbar"},
        {"label": "Horizontal Bar chart", "value": "hbar"},
        {"label": "Scatter", "value": "scatter"},
        {"label": "Histogram", "value": "histogram"},
    ]

    graph_type_component = dcc.Dropdown(
        id="graph-type",
        options=grap_type_options,
        value="line",
        clearable=False,
        placeholder="Graph type",
    )

    x_component = dcc.Dropdown(
        id="x-axis",
        options=[],
        clearable=True,
        placeholder="X axis",
    )
    y_component = dcc.Dropdown(
        id="y-axis",
        options=[],
        clearable=True,
        placeholder="Y axis",
    )

    return [
        row(
            [
                col(
                    "three columns",
                    children=[
                        html.H4("Visualization configuration"),
                        # graph type
                        graph_type_component,
                        x_component,
                        y_component,
                    ],
                ),
                col(
                    "nine columns",
                    children=[
                        dcc.Loading(
                            id="loading-graph-content",
                            type="graph",
                            children=html.Div(
                                id="graph_content",
                                children=html.P("- no graph yet -"),
                                style={
                                    "minHeight": "40px",
                                    "textAlign": "center",
                                    "paddingTop": "5px",
                                },
                            ),
                        )
                    ],
                ),
            ]
        )
    ]
