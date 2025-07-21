from pathlib import Path

import pandas as pd
from pandas import DataFrame


class DataFrameUtil:
    @staticmethod
    def get_dataframe(file_path:Path) -> DataFrame | None:
        try:
            if file_path.suffix.lower() in ['xlsx', 'xls']:
                return pd.read_excel(file_path, engine='openpyxl')
            elif file_path.suffix.lower() in ['csv', 'txt']:
                return pd.read_csv(file_path, encoding='utf-8')
        except Exception as e:
            raise RuntimeError(str(e))