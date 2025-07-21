import json
from typing import Any

from . import resource_path

def loader(file_with_path: str) -> dict[str, str] | None:
    final_path = resource_path.resource_path(file_with_path)
    with open(final_path, 'r', encoding='utf8') as file:
        data_data:dict[str:str] = json.load(file)
    if data_data:
        return data_data