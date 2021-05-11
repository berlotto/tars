"""Método que contém métodos auxiliares para tratamento dos dados utilizados
nos componentes de tela e de Store
"""
import base64
import io

import pandas as pd
from pandas.api.types import is_numeric_dtype

# from core.compress import compressStringToBytes, decompressBytesToString


def to_session(df: pd.DataFrame):
    # Salva o conteúdo em memória, de forma comprimida
    # return compressStringToBytes(df.to_json())
    return df.to_json()


def from_session(df_data) -> pd.DataFrame:
    # Converte da saída de `to_json` para DataFrame
    # normal_json = decompressBytesToString(df_data)
    return pd.read_json(df_data)


def parse_file_contents(contents, filename, date):

    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            try:
                print("Lendo arquivo...")
                csv_content = io.StringIO(decoded.decode("utf-8"))
            except UnicodeDecodeError:
                print("Erro de encoding UTF-8, tentando iso-8859-1...")
                csv_content = io.StringIO(decoded.decode("iso-8859-1"))

            csv_content.seek(0)
            df_semicolon = pd.read_csv(csv_content, parse_dates=True, nrows=1, sep=";")
            csv_content.seek(0)
            df_comma = pd.read_csv(csv_content, parse_dates=True, nrows=1, sep=",")
            csv_content.seek(0)
            if df_comma.shape[1] > df_semicolon.shape[1]:
                df = pd.read_csv(csv_content, parse_dates=True, sep=",")
            else:
                df = pd.read_csv(csv_content, parse_dates=True, sep=";")

        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), parse_dates=True)
        else:
            return None

    except Exception as e:
        print(e)
        raise Exception("There was an error processing this file.")

    return df


def get_dt_colunas_data(df):
    cols_data = [
        {"coluna": k, "tipo": str(v), "excluir": False} for k, v in df.dtypes.items()
    ]
    return cols_data


def modify_original_df(original_df, config_data):
    # {'coluna': 'id', 'tipo': 'int64', 'excluir': False, 'rename': 'nome', 'converter': 'int64', 'fillna': 'mean'}
    new_df = original_df.copy()
    for col in config_data:
        colname = col.get("coluna")
        currentname = col.get("coluna")
        if not col.get("excluir", False):
            if col.get("rename", None):
                rename_to = col.get("rename")
                new_df.rename(columns={colname: rename_to}, inplace=True)
            if col.get("fillna", None):
                fillna_with = col.get("fillna")
                isnum = is_numeric_dtype(new_df[currentname])
                try:
                    if isnum and fillna_with == "mean":
                        new_df[currentname] = new_df[currentname].fillna(
                            new_df[currentname].mean()
                        )
                    elif isnum and fillna_with == "max":
                        new_df[currentname] = new_df[currentname].fillna(
                            new_df[currentname].max()
                        )
                    elif isnum and fillna_with == "min":
                        new_df[currentname] = new_df[currentname].fillna(
                            new_df[currentname].min()
                        )
                    else:
                        new_df[currentname] = new_df[currentname].fillna(fillna_with)
                except TypeError as notnumeric:
                    print(
                        f"Erro calculando o mean/max/min para o fillna da coluna {currentname}"
                    )
                    print(notnumeric)
            if col.get("converter"):
                convert_to = col.get("converter")
                new_df[currentname] = new_df[currentname].astype(convert_to)
        else:  # -> Excluir
            new_df.drop(columns=[colname], inplace=True)
    return new_df


def value_as_type(df, column_name, value):
    """Try to convert a value to a type compatible with the column type"""
    try:
        if is_numeric_dtype(df[column_name]):
            return float(value)
        else:
            return str(value)
    except ValueError:
        return value
