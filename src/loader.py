import pandas as pd
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal
from pathlib import Path


# defining the data source using dataclass method, for type checking and validation
@dataclass
class Source:
    """ 
    Defining the data source and attributes
    Args:
        file_path: Path to the file
        file_type: Type of the file (csv or json)
    """
    file_path: Path
    file_type: Literal['csv', 'json']

class LoaderToPandas:
    """ 
    Loader class to load data from source to a pandas dataframe 
    
    Returns:
        pandas dataframe
    """
    def __init__(self, source: Source):
        self.source = source
    
    # use pandas read_cvs and read_json, only csv and json are supported as defined in dataclass method
    def load(self) -> pd.DataFrame:
        """ ingest json and/or csv file into pandas dataframe
        returns: pandas dataframe """
        match self.source.file_type:
            case'csv':
                return pd.read_csv(self.source.file_path)
            case 'json':
                return pd.read_json(self.source.file_path)
            case _:
                raise Exception (f"Error: {type(self.source.file_type)}: {self.source.file_type} from Path: {self.source.file_path}") # not needed but good to have 
          
def load_database(self) -> pd.DataFrame:
    pass

    def load_aws_s3(self) -> pd.DataFrame:
        pass

