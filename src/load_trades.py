import pandas as pd
from pathlib import Path


class LoaderToPandas:
    """Load a CSV or JSON file into a pandas DataFrame.
    args: file_path: Path
        csv or json file type
    returns: pandas dataframe
    """
    def __init__(self, file_path: Path):
        self.file_path = file_path # path object file path attribute

    def load(self) -> pd.DataFrame:
        """ ingest json and/or csv file into pandas dataframe
        returns: pandas dataframe """
        match self.file_path.suffix.lower():
            case '.csv':
                return pd.read_csv(self.file_path)
            case '.json':
                return pd.read_json(self.file_path)
            case _:
                raise Exception (f"Invalid file type: {self.file_path.suffix.lower()} from Path: {self.file_path}, needs JSON or CSV as input") # not needed but good to have 
          

def normalize_column_names(df_csv: pd.DataFrame, df_json: pd.DataFrame) -> pd.DataFrame: # to do later LIST of dataframes
    """ Normalize the column names of the dataframe
    args: df_csv, df_json
    returns: df 
        normalized column names 
    """
    print(" column names from csv file: ", df_csv.columns.tolist())
    print(" column names from json file: ", df_json.columns.tolist())
    for col in df_csv.columns:
        if col not in df_json.columns:
            print(f"Column {col} not found in json file")
        else:
            print(f"Column {col} found in json file")
    for col in df_json.columns:
        if col not in df_csv.columns:
            print(f"Column {col} not found in csv file")
