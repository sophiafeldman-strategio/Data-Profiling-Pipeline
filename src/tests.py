import unittest
from pathlib import Path
from load_trades import LoaderToPandas

# data located at ROOT/data/... (parents[1] to access data folder needed for tests)
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TYPES = {
    "trade_id": "object",
    "instrument_id": "object",
    "instrument_type": "object",
    "trade_date": "object",
    "buyer": "object",
    "seller": "object",
    "quantity": "int64",
    "price": "float64",
    "trade_status": "object",
}


class TestLoadTrades(unittest.TestCase):
    ''' Test the load_trades to ensure data matches expected types and column names for both json (post flattening) and csv'''
    def test_records_match_names_and_types(self):
        df_csv = LoaderToPandas(ROOT / "data/meridian_trades_small.csv").load()
        df_json = LoaderToPandas(ROOT / "data/meridian_trades_small.json").load()

        self.assertEqual(list(df_csv.columns), list(df_json.columns))
        for record in (df_csv, df_json): 
            actual = {column: str(dtype) for column, dtype in record.dtypes.items()}
            # compare record types to expected types
            self.assertEqual(actual, EXPECTED_TYPES)

if __name__ == "__main__":
    unittest.main()
