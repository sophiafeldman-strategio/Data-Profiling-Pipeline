# Build a Python data profiling pipeline 

### Purpose: 
loads the Meridian Capital Markets client records dataset, identifies data quality issues, and produces a structured report summarising your findings.


### Tuesday - Python Fundamentals & Initial Development
- Revise Python fundamentals covering functions, data structures, control flow, file I/O,
and error handling.
- Start developing your Meridian data profiling pipeline using Pandas:
- Load the provided CSV and JSON datasets
- Learn how to combine the datasets
- Profile the dataset for data quality issues
- Identify null counts, data types, value ranges, and duplicate rows
- Generate a formatted text report summarising your findings.

### Wednesday - Git Workflow, Pipeline Structure & Finalisation
- Revise Git setups covering branching, merging, pull requests, and code reviews. Open a
pull request for your work and review a peer’s implementation.
- Continue developing and finalising your pipeline:
- Structure into discrete functions (ie, load, validate, profile, report)
- Include docstrings for each function
- Handle missing or unreadable input files
- Produce a clear and structured report of data quality findings
- Review your profiling findings using the five data quality dimensions: completeness,
consistency, accuracy, timeliness, validity
- Categorise your identified findings according to the relevant data quality dimensions.
- Complete peer code review, leaving at least 3 constructive comments
- Write a user story and acceptance criteria for your deliverable, framed as a requirement
from a Meridian product owner.

### Final Deliverable:
- A functional Python data profiling pipeline committed to Github.
- A modular implementation with separate functions and docstrings.
- Handling of missing or unreadable input files.
- A formatted report summarising your findings.
- An open pull request your pair programming partner and Nelli as reviewers.

# Libraries
- pandas >= 2.3, listed in `requirements.txt`. 
- Python standard library: `json` to parse the trade file, `pathlib` for file paths, `datetime` for the report date, and `unittest` for the load test.

