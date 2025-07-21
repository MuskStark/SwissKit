import numpy as np
import os
import pandas as pd
import re
import yaml
from pathlib import Path


def extract_month(filename):
    match = re.search(r'(\d)月', filename)
    return int(match.group(1)) if match else 0

class Tutil:

    @classmethod
    def load_config(cls, config_path:str):
        with open(config_path, 'r', encoding='utf-8', errors='replace') as f:
            config = yaml.safe_load(f)
            f.close()
            return config

    @classmethod
    def os_mkdir(cls, path_list:[Path]):
        for path in path_list:
            if not path.exists():
                os.makedirs(path)

    @classmethod
    def file_to_dataframe(cls, file_path: Path, **kwargs):
        extension = file_path.suffix
        if extension in ['.csv']:
            return pd.read_csv(file_path, **kwargs)
        if extension in ['.xlsx', '.xls']:
            return pd.read_excel(file_path, **kwargs)
        if extension in ['.json']:
            return pd.read_json(file_path, **kwargs)
        else:
            raise ValueError(f"不支持{extension}该文件格式")

    @classmethod
    def remove_duplicate_columns(cls, df:pd.DataFrame, reserved_cols='_x'):
        for col in df.columns:
            if col.endswith('_x') or col.endswith('_y'):
                if col.endswith(reserved_cols):
                    df.rename(columns={col: col[:-2]}, inplace=True)
                else:
                    df.drop(columns=[col], inplace=True)

