"""Método que contém métodos auxiliares para tratamento dos dados utilizados
nos componentes de tela e de Store
"""
import base64
import pandas as pd
import io
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

def to_session(df: pd.DataFrame): 
    return df.to_json()

def from_session(df_data) -> pd.DataFrame: 
    # Converte da saída de `to_json` para DataFrame
    return pd.read_json(df_data)


def parse_file_contents(contents, filename, date):

    content_type, content_string = contents.split(',')
    cols_data = []  # Same structure for dt_colunas 
    
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')),
                parse_dates=True)
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded),
                parse_dates=True)
        else:
            return None

    except Exception as e:
        print(e)
        raise Exception('There was an error processing this file.')
    
    return df

def get_dt_colunas_data(df):
    cols_data = [ {'coluna':k,'tipo':str(v),'excluir':False} 
                  for k,v in df.dtypes.items() ]
    return cols_data
