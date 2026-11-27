from load_trades import LoaderToPandas
from pathlib import Path
from transform_df import concat_df
from profiler import REFERENCE_PATH, summary_stats

def main():
    """ create an instance of LoaderToPandas and load data from /tests/data """
    csv_path = Path("tests/data/meridian_trades_small.csv")
    json_path = Path("tests/data/meridian_trades_small.json")
    try:
        df_csv = LoaderToPandas(csv_path).load()
    except Exception as e:
        print(f"Error loading file, invalid or does not exist: {e}")
        return
    try:
        df_json = LoaderToPandas(json_path).load()
    except Exception as e:
        print(f"Error loading file, invalid or does not exist: {e}")
        return
    print(df_csv.head())
    print(df_json.head())
    print(f' column names are: {df_csv.columns}') 
    print(f' column names are: {df_json.columns}') 
    print(f' df_csv shape is: {df_csv.shape} and type: {type(df_csv)}')
    print(f' df_json shape is: {df_json.shape} and type: {type(df_json)}')
    df = concat_df([df_csv, df_json])
    print(f' New df shape is: {df.shape}')
    print(summary_stats(df, REFERENCE_PATH))

        
if __name__ == "__main__":
    main()