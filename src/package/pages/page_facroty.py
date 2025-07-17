import flet as ft

from .page.excel_split_v2 import ExcelSplitPageV2
from .page.guan_hu_match import Relationship
from .page.innovation import Innovation
from .page.odap_formater import ODAPFormater
from .page.odap_search_value import ODAPSearchValue


class PageFactory:
    @staticmethod
    def create_page(index:int, page:ft.Page):
        if index == 0:
            return ODAPFormater(page)
        elif index == 1:
            return ExcelSplitPageV2(page)
        elif index == 2:
            return ODAPSearchValue(page)
        else:
            raise ValueError("Unknown product type")