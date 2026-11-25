# Meridian Data Profiling Pipeline 
Pipeline loads and assesses securities trade blotter data from **Meridian Capital Markets** building a profiler for data quality assessment 

# Installation 
Clone repo and install dependencies
```bash
git clone https://github.com/sophiafeldman-strategio/Data-Profiling-Pipeline.git
cd Data-Profiling-Pipeline
pip install -r requirements.txt
python src/main.py
```
# Usage 
Run `Main.py` profiler outputs to `/output/summary_stats.md` for user review 

# Data 
`input files: data/meridian_trades_small.csv`
`data/meridian_trades_small.json`
`data/data_info/SCHEMA.md`

*Note: data is synthetic*

# Project structure
```text
.
├── src/
│   ├── main.py            # loads data, combines it, writes the report
│   ├── load_trades.py     # reads the CSV and JSON files
│   ├── transform_df.py    # combines the two datasets
│   ├── profiler.py        # data quality checks
│   └── tests.py
├── data/
│   ├── meridian_trades_small.csv
│   ├── meridian_trades_small.json
│   └── data_info/         # schema and field notes
├── output/
│   └── summary_stats.md   # profiling report
├── tests/
│   └── tests.py
├── requirements.txt
└── README.md
```

# Author
**Sophia Feldman**
Data profiling pipeline for Meridian Capital Markets.

[GitHub](https://github.com/sophiafeldman-strategio)
