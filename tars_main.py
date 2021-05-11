# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from pandas.api.types import is_numeric_dtype, is_string_dtype

from core.components import (
    get_columns_tab_components,
    get_data_tab_components,
    get_information_components,
    get_numeric_information_gui,
    get_sample_df_data_children,
    get_string_information_gui,
    get_tab_filtering_components,
    get_table_dfcolumns,
    get_vis_tab_components,
)
from core.data import (
    from_session,
    get_dt_colunas_data,
    modify_original_df,
    parse_file_contents,
    to_session,
    value_as_type,
)

# CSS: http://getskeleton.com/
others = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "/assets/custom.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css",
]

app = dash.Dash(__name__, external_stylesheets=others)
# Important configuration to deal with non-created components
app.config["suppress_callback_exceptions"] = True


app.layout = html.Div(
    id="container",
    children=[
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="nine columns",
                    children=[
                        html.H2(
                            className="special-title",
                            children=[
                                html.I(className="fas fa-bars fa-rotate-90"),
                                " TARS",
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="three columns text-center",
                    children=[
                        dcc.Upload(
                            id="upload-data",
                            children=[
                                html.Button(
                                    "Load data",
                                    className="button button-primary",
                                    title="CSV e Excel files only",
                                )
                            ],
                            style={"textAlign": "center"},
                            multiple=False,
                        ),
                    ],
                ),
            ],
        ),
        dcc.Store(id="store_original_df", storage_type="memory"),
        dcc.Store(id="store_modified_df", storage_type="memory"),
        dcc.Store(id="store_filters", storage_type="memory"),
        dcc.Tabs(
            id="tabs-main",
            value="tab-data",
            children=[
                dcc.Tab(
                    label="Data", value="tab-data", children=get_data_tab_components()
                ),
                dcc.Tab(
                    label="Columns",
                    value="tab-columns",
                    children=get_columns_tab_components(),
                ),
                dcc.Tab(
                    label="Informations",
                    value="tab-info",
                    id="tab-info",
                    children=get_information_components(),
                ),
                dcc.Tab(
                    label="Filter data",
                    value="tab-filter",
                    id="tab-filter",
                    children=get_tab_filtering_components(),
                ),
                dcc.Tab(
                    label="Visualization",
                    value="tag-visualizacao",
                    children=get_vis_tab_components(),
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("sample-file-content", "children"),
    Input("store_original_df", "data"),
    prevent_initial_call=True,
)
def on_load_sample_file_update_store_original(original_df_json):
    """Tab:Data, Section: Table with first rows"""
    original_df = from_session(original_df_json)
    return get_sample_df_data_children(original_df)


@app.callback(
    Output("dt_colunas", "data"),
    Input("store_original_df", "data"),
    prevent_initial_call=True,
)
def on_update_store_original_show_sample_data(original_df_json):
    """Tab:Colunas, Section: Deal with the dataframe columns"""
    original_df = from_session(original_df_json)
    return get_dt_colunas_data(original_df)


@app.callback(
    Output("original_df_cols", "children"),
    Input("store_original_df", "data"),
    prevent_initial_call=True,
)
def on_update_store_original_update_columns_original_configuration_data(
    original_df_json,
):
    """Tab:Columns, Section: Original Configuration"""
    original_df = from_session(original_df_json)
    columns_data = get_dt_colunas_data(original_df)
    return get_table_dfcolumns(columns_data, id="origin", df=original_df)


@app.callback(
    Output("tab-info", "children"),
    Input("store_modified_df", "data"),
    prevent_initial_call=True,
)
def on_update_modified_df_update_informations_fields(original_df_json):
    """Tab:Information, Section: Combobox of column"""
    modified_df = from_session(original_df_json)
    return get_information_components(modified_df)


@app.callback(
    Output("tab-filter", "children"),
    Input("store_modified_df", "data"),
    prevent_initial_call=True,
)
def on_update_modified_df_update_update_filterdata_gui(original_df_json):
    """Tab:Filter Data, Section: Fields and Data"""
    modified_df = from_session(original_df_json)
    return get_tab_filtering_components(modified_df)


@app.callback(
    Output("data-table-filter", "data"),
    Input("apply-filter-button", "n_clicks"),
    State("data-table-filter", "data"),
    State("inputfiltervalue", "value"),
    State("dropdownoperador", "value"),
    State("dropdowncolumns", "value"),
    prevent_initial_call=True,
)
def on_button_filter_click_update_table_data(
    n_clicks, filters_list, filter_value, filter_comp, filter_field
):
    """Tab:Filter & Clean, Section: Button 'bolt'"""
    if not filter_field or not filter_value or not filter_field.strip():
        raise PreventUpdate()

    filter_config = {"field": filter_field, "comp": filter_comp, "value": filter_value}

    if filter_config not in filters_list:
        filters_list.append(filter_config)

    return filters_list


@app.callback(
    Output("inputfiltervalue", "disabled"),
    Output("inputfiltervalue", "value"),
    Input("dropdownoperador", "value"),
    State("inputfiltervalue", "value"),
)
def on_change_filter_operator_change_value_enable(comparator_value, value_value):
    if comparator_value in ("isnull", "notnull"):
        return (True, "")
    else:
        return (False, value_value)


@app.callback(
    Output("store_original_df", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
    prevent_initial_call=True,
    suppress_callback_exceptions=True,
)
def on_load_file_save_content_to_state(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        try:
            df = parse_file_contents(list_of_contents, list_of_names, list_of_dates)
            return to_session(df)
        except Exception:
            raise PreventUpdate
    else:
        raise PreventUpdate


@app.callback(
    Output("store_modified_df", "data"),
    Input("store_original_df", "data"),
    Input("dt_colunas", "data"),
)
def on_update_content_on_state_update_modified_df(original_df_json, data):
    """Change the data of the Store for modified df"""
    if not data:
        raise PreventUpdate

    original_df = from_session(original_df_json)
    modified_df = modify_original_df(original_df, data)
    return to_session(modified_df)


@app.callback(
    Output("changed_df_cols", "children"),
    Input("store_modified_df", "data"),
    Input("dt_colunas", "data"),
)
def on_change_modified_df_update_columns_result_configuration(modified_df_json, data):
    """Show the modified columns in the Result configuration"""
    if not data:
        raise PreventUpdate

    modified_df = from_session(modified_df_json)

    return get_table_dfcolumns(data, id="new", df=modified_df)


@app.callback(
    Output("information-content", "children"),
    Input("store_modified_df", "data"),
    Input("selected_column", "value"),
    prevent_initial_call=True,
)
def on_change_modified_df_state_update_information_columns(df_json, info_column):
    """Show information when column dropdown, in Information tab is changed."""
    info_children = []

    if df_json and info_column != "-":
        df = from_session(df_json)

        dados = df[info_column]

        if is_numeric_dtype(dados):
            info_children = get_numeric_information_gui(dados, info_column)
        elif is_string_dtype(dados):
            info_children = get_string_information_gui(dados, info_column)
        # TODO: Mostrar mais tipos
        # elif is_bool_dtype(dados):
        #     info_children = get_bool_information_gui(dados, info_column)
        # elif is_datetime64_any_dtype(dados):
        #     info_children = get_datetime_information_gui(dados, info_column)

    return info_children


@app.callback(
    Output("modified_filtered_table", "data"),
    Input("data-table-filter", "data"),
    State("store_modified_df", "data"),
)
def on_add_filter_update_table_data(filter_data, modified_df_json):

    df = pd.DataFrame()
    if modified_df_json:
        df = from_session(modified_df_json)

    if not df.empty and filter_data:

        for filter_row in filter_data:
            print(
                f"FILTRANDO: {filter_row['field']}->{filter_row['comp']}->{filter_row['value']}"
            )
            typed_value = value_as_type(df, filter_row["field"], filter_row["value"])
            if filter_row["comp"] == "eq":
                df = df[df[filter_row["field"]] == typed_value]
            if filter_row["comp"] == "ne":
                df = df[df[filter_row["field"]] != typed_value]
            if filter_row["comp"] == "gt":
                df = df[df[filter_row["field"]] > typed_value]
            if filter_row["comp"] == "ge":
                df = df[df[filter_row["field"]] >= typed_value]
            if filter_row["comp"] == "lt":
                df = df[df[filter_row["field"]] < typed_value]
            if filter_row["comp"] == "le":
                df = df[df[filter_row["field"]] <= typed_value]

    return df.to_dict("records") if df is not None else []


@app.callback(
    Output("x-axis", "options"),
    Input("modified_filtered_table", "data"),
    Input("y-axis", "value"),
    prevent_initial_call=True,
)
def on_modify_df_load_columns_x_axis(filtered_data, y_selected):

    df = pd.DataFrame.from_records(filtered_data)
    return [{"label": c, "value": c} for c in df.columns if c != y_selected]


@app.callback(
    Output("y-axis", "options"),
    Input("modified_filtered_table", "data"),
    Input("x-axis", "value"),
    prevent_initial_call=True,
)
def on_modify_df_load_columns_y_axis(filtered_data, x_selected):

    df = pd.DataFrame.from_records(filtered_data)
    return [{"label": c, "value": c} for c in df.columns if c != x_selected]


@app.callback(
    Output("graph_content", "children"),
    Input("modified_filtered_table", "data"),
    Input("graph-type", "value"),
    Input("x-axis", "value"),
    Input("y-axis", "value"),
    prevent_initial_call=True,
)
def on_add_filter_update_visualization_tab(filtered_data, graph_type, x_col, y_col):
    print("Mostrando um grafico do tipo:", graph_type)

    df = pd.DataFrame.from_records(filtered_data)

    conditions = [df is not None, not df.empty, graph_type, x_col, y_col]
    print(all(conditions))
    print(conditions)

    if all(conditions):

        if graph_type == "line":
            fig = px.line(df, y=y_col, x=x_col)
        elif graph_type == "vbar":
            fig = px.bar(df, y=y_col, x=x_col)
        elif graph_type == "hbar":
            fig = px.bar(df, y=y_col, x=x_col, orientation="h")
        elif graph_type == "scatter":
            fig = px.scatter(df, y=y_col, x=x_col)
        # elif graph_type == 'pie':
        #     fig = px.pie(df, values='open', names='country', title='Population of European continent')
        elif graph_type == "histogram":
            fig = px.histogram(df, x=x_col)

        graph = dcc.Graph(id="vis-plot", figure=fig)

        return graph
    else:
        return []


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
