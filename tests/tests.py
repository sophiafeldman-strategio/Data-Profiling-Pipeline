import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

# sample files live in tests/data, next to this file
DATA = Path(__file__).resolve().parent / "data"
EXPECTED_TYPES = {
    "trade_id": "str",
    "instrument_id": "str",
    "instrument_type": "str",
    "trade_date": "str",
    "buyer": "str",
    "seller": "str",
    "quantity": "int64",
    "price": "float64",
    "trade_status": "str",
}


SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from load_trades import LoaderToPandas
from profiler import ALLOWED_VALUES, REFERENCE_PATH, WEIGHT, invalid_category_count, load_reference, quality_scores
from transform_df import concat_df

class TestLoadTrades(unittest.TestCase):
    """ Test the load_trades to ensure data matches expected types and column names for both json (post flattening) and csv"""
    def test_records_match_column_names_and_types(self):
        df_csv = LoaderToPandas(DATA / "meridian_trades_small.csv").load()
        df_json = LoaderToPandas(DATA / "meridian_trades_small.json").load()

        print(f"csv columns: {list(df_csv.columns)}")
        print(f"json columns: {list(df_json.columns)}")
        self.assertEqual(list(df_csv.columns), list(df_json.columns))
        for record in (df_csv, df_json):
            actual = {column: str(dtype) for column, dtype in record.dtypes.items()}
            print(f"actual types: {actual}")
            # compare record types to expected types
            self.assertEqual(actual, EXPECTED_TYPES)

    def test_invalid_file_type_raises(self):
        """ Test the load_trades to ensure an exception is raised for invalid file types"""
        with self.assertRaises(Exception) as caught:
            LoaderToPandas(Path("trades.txt")).load() # try txt (invalid file type)
        print(f"invalid file type raised: {caught.exception}")
        self.assertIn("Invalid file type", str(caught.exception))

    def test_empty_csv_raises(self):
        with tempfile.TemporaryDirectory() as directory:
            empty = Path(directory) / "empty.csv"
            empty.write_text("")
            with self.assertRaises(EmptyDataError) as caught:
                LoaderToPandas(empty).load()
            print(f"empty csv raised: {caught.exception}")

    def test_broken_json_raises(self):
        with tempfile.TemporaryDirectory() as directory:
            broken = Path(directory) / "broken.json"
            broken.write_text("{")
            with self.assertRaises(json.JSONDecodeError) as caught:
                LoaderToPandas(broken).load()
            print(f"broken json raised: {caught.exception}")


class TestAllowedValues(unittest.TestCase):
    def test_counts_values_outside_the_schema_lists(self):
        frame = pd.DataFrame({
            "instrument_type": ["Equity", "Option", "Bond"],
            "trade_status": ["EXECUTED", "NOPE", "SETTLED"],
        })
        type_count = invalid_category_count(frame["instrument_type"], ALLOWED_VALUES["instrument_type"])
        status_count = invalid_category_count(frame["trade_status"], ALLOWED_VALUES["trade_status"])
        print(f"invalid instrument_type count: {type_count}")
        print(f"invalid trade_status count: {status_count}")
        self.assertEqual(type_count, 1)
        self.assertEqual(status_count, 1)


class TestReferenceData(unittest.TestCase):
    """Filled instrument ids must match securities on the reference file (data_info/meridian_reference_data.csv) containing 30 unique instrument ids"""

    def test_reference_file_is_the_instrument_master(self):
        """The reference file is the 30-security list."""
        reference = load_reference(Path(__file__).resolve().parents[1] / "data_info" / "meridian_reference_data.csv")
        unique_ids = reference["instrument_id"].nunique()
        print(f"unique instrument ids: {unique_ids}")
        print(f"MRCX present: {'MRCX' in set(reference['instrument_id'])}")
        self.assertEqual(unique_ids, 30)
        self.assertIn("MRCX", set(reference["instrument_id"]))

    def test_unknown_id_and_type_mismatch_are_counted(self):
        """An id that is not on the reference list, and a known id with the wrong type, are both counted."""
        reference = load_reference(Path(__file__).resolve().parents[1] / REFERENCE_PATH)
        frame = pd.DataFrame({
            "trade_id": ["TRD-1", "TRD-2", "TRD-3"],
            "instrument_id": ["MRCX", "ZZZZ", "MRCX"],
            "instrument_type": ["Equity", "Equity", "Bond"],
            "trade_date": ["2025-01-02", "2025-01-02", "2025-01-02"],
            "buyer": ["A", "A", "A"],
            "seller": ["B", "B", "B"],
            "quantity": [100, 100, 100],
            "price": [10.0, 10.0, 10.0],
            "trade_status": ["EXECUTED", "EXECUTED", "EXECUTED"],
        })
        scores = quality_scores(frame, reference)
        print(f"unknown_instrument: {scores['unknown_instrument']}")
        print(f"type_mismatch: {scores['type_mismatch']}")
        print(f"overall: {scores['overall']}")
        self.assertEqual(scores["unknown_instrument"], 1)
        self.assertEqual(scores["type_mismatch"], 1)
        weighted = sum(check["weight"] * check["score"] for check in scores["checks"]) / sum(check["weight"] for check in scores["checks"])
        self.assertAlmostEqual(scores["overall"], weighted)

    def test_price_and_ids_weigh_more_than_labels(self):
        """Trade id, instrument id, and price weigh 3. Buyer and seller weigh 2. Instrument type weighs 1. Ensure weights are as expected.
        Reference weights are defined in profiler.py"""
        print(f"weights: {WEIGHT}")
        self.assertEqual(WEIGHT["trade_id"], 3)
        self.assertEqual(WEIGHT["instrument_id"], 3)
        self.assertEqual(WEIGHT["price"], 3)
        self.assertEqual(WEIGHT["buyer"], 2)
        self.assertEqual(WEIGHT["seller"], 2)
        self.assertEqual(WEIGHT["instrument_type"], 1)
        self.assertLess(WEIGHT["instrument_type"], WEIGHT["trade_id"])


class TestConcat(unittest.TestCase):
    """ Test the concat dataframe function on two test dataframes: a and b
    Args:
        a: pd.DataFrame
        b: pd.DataFrame
    Returns:
        pd.DataFrame: combined dataframe
    """
    def test_concat_stacks_rows_and_resets_index(self):
        first = pd.DataFrame({"trade_id": ["a"]})
        second = pd.DataFrame({"trade_id": ["b"]})
        combined = concat_df([first, second])
        print(f"combined trade_id: {list(combined['trade_id'])}")
        print(f"combined index: {list(combined.index)}")
        self.assertEqual(list(combined["trade_id"]), ["a", "b"])
        self.assertEqual(list(combined.index), [0, 1])

if __name__ == "__main__":
    unittest.main()
