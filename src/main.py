from loader import LoaderToPandas
from pathlib import Path
from loader import Source

def main():
    """ create an instance of LoaderToPandas and load data from /data """
    source_csv = Source(Path('data/meridian_trades_small.csv'),"csv")
    source_json = Source(Path('data/meridian_trades_small.json'),"json")
    try:
        df_csv = LoaderToPandas(source_csv).load()
    except Exception as e:
        print(f"Error loading file, invalid or does not exist: {e}")
        return
    try:
        df_json = LoaderToPandas(source_json).load()
    except Exception as e:
        print(f"Error loading file, invalid or does not exist: {e}")
        return
    print(df_csv.head())
    print(df_json.head())

if __name__ == "__main__":
    main()