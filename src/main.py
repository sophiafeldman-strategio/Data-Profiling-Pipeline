from load_trades import LoaderToPandas
from pathlib import Path
from load_trades import flatten_json

def main():
    """ create an instance of LoaderToPandas and load data from /data """
    csv_path = Path("data/meridian_trades_small.csv")
    json_path = Path("data/meridian_trades_small.json")
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

if __name__ == "__main__":
    main()