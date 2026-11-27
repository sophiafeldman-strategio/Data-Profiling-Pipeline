import pandas as pd
from pathlib import Path
import json

COLUMN_MAP = {
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
            return pd.DataFrame(flatten_json(json_data)).rename(columns=COLUMN_MAP) # flatten the json data and turn into dataframe
        case _:
            raise Exception (f"Invalid file type: {file_path.suffix.lower()} from Path: {file_path}, needs JSON or CSV as input") # not needed but good to have 


# once file is read, data becomes list of dictionaries
def flatten_json(json_records: list[dict]) -> list[dict]:
    """ Normalize the column names of the dataframe
    args: list[dict]
    returns: list[dict]
        flattens nested json records into list of dictionaries
    """
    flattened_records = [] #completed flattened records stored here
    for record in json_records:
        already_flattened_record = {} 
        for key, value in record.items(): 
                if isinstance(value, dict): # isinstance tell apart dict and str (true when dict)
                    already_flattened_record.update(value) # is a dictionary, need to flatten 
                else:
                    already_flattened_record[key] = value # store directly, not dictionary
        flattened_records.append(already_flattened_record)
    print(f'Count of flattened records from : {len(flattened_records)}, expected {len(json_records)}')
    return flattened_records # return the list of flattened records

  
  # revisit line 53 
  # revisit how functions are named 
