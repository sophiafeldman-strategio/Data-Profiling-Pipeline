import pandas as pd


def concat_df(DfList: list[pd.DataFrame]) -> pd.DataFrame:
    
    """ Transforms the data by concatenating the dataframes
    args: List 
        list of pandas dataframes
    returns: df_concat
    """
    print(f"Concatenating {len(DfList)} dataframes")
    return pd.concat(DfList, ignore_index=True) # ascending index order


