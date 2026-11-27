from load_trades import LoaderToPandas
from pathlib import Path
from transform_df import concat_df
from profiler import REFERENCE_PATH, write_summary_stats
from jproperties import Properties

# -------------- load the csv and json paths from config.properties ----------------------
config_properties = Properties()
with open('config.properties', 'rb') as config_file:
    config_properties.load(config_file)

def main():
    """ create an instance of LoaderToPandas and load data from /tests/data """
# -------------- load the data from the csv and json files (from config.properties)--------------
    csv_path = Path(config_properties.get('csv_path').data)
    json_path = Path(config_properties.get('json_path').data)
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

# -------------- print information about dataframes --------------
    print(df_csv.head())
    print(df_json.head())
    print(f' column names are: {df_csv.columns}') 
    print(f' column names are: {df_json.columns}') 
    print(f' df_csv shape is: {df_csv.shape} and type: {type(df_csv)}')
    print(f' df_json shape is: {df_json.shape} and type: {type(df_json)}')
 
# -------------- concat the two dataframes ------------------------
    df = concat_df([df_csv, df_json])
    print(f' New df shape is: {df.shape}')

# -------------- generate the summary statstistics file and print output file path --------------
    summary_stats_path = write_summary_stats(df, REFERENCE_PATH)
    print(f' Report path = {summary_stats_path}')

        
if __name__ == "__main__":
    main()