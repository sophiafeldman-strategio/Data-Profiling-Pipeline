import pandas as pd
from pathlib import Path
import json


# ---- using csv as desired column names, the column map is for json normalization and column name standardization ----------
COLUMN_MAP_JSON = {
    "tradeReference": "trade_id",
    "securityCode": "instrument_id",
    "securityType": "instrument_type",
    "executionDate": "trade_date",
    "buyingFirm": "buyer",
    "sellingFirm": "seller",
    "units": "quantity",
    "executionPrice": "price",
    "settlementStatus": "trade_status",
}

def load_trades(file_path: Path) -> pd.DataFrame:
    """Load a CSV or JSON file into a pandas DataFrame.
    args: file_path: Path
        csv or json file type
    returns: pandas dataframe
    """
    match file_path.suffix.lower():
        case '.csv':
            return pd.read_csv(file_path)
        case '.json':
            json_data = json.loads(file_path.read_text()) # parse file into list of records (still nested)
            flatten_dictonaries(json_data) 
            df = pd.DataFrame(json_data)
            return rename_columns(df, COLUMN_MAP_JSON)
        case _:
            raise Exception (f"Invalid file type: {file_path.suffix.lower()} from Path: {file_path}, needs JSON or CSV as input") # not needed but good to have 


def rename_columns(df: pd.DataFrame, column_map: dict[str, str]) -> pd.DataFrame:
    """Rename matching columns one at a time on this DataFrame.
    Each inplace rename replaces that column's label. The row data stays put.
    """
    for old_name, new_name in column_map.items():
        if old_name in df.columns:
            df.rename(columns={old_name: new_name}, inplace=True)
    return df


# once file is read, data becomes list of dictionaries
def flatten_dictonaries(dictonaries: list[dict]) -> None: 
    """ Flatten the nested dictonary records into a list of flat dictionaries in place
    args: list[dict]
    returns: None (modifies in place to become flat dictionaries)
    note: only handles one level of nesting
    """
    for i, nested_dict in enumerate(dictonaries):
        flat = {} 
        for key, value in nested_dict.items(): 
                if isinstance(value, dict): # isinstance tell apart dict and str (true when dict)
                    flat.update(value) # flatten one level, add all keys in bulk
                else:
                    flat[key] = value # store directly, already at top level (not dictionary)
        dictonaries[i] = flat
    print(f'Count of flattened dictonaries from : {len(dictonaries)}')
