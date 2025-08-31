import flet as ft

from .page.email.email_main import Email
from .page.excel_split_v2 import ExcelSplitPageV2
from .page.odap_formater import ODAPFormater
from .page.odap_search_value import ODAPSearchValue


class PageFactory:
    @staticmethod
    def create_page(index: int, page: ft.Page):
        if index == 0:
            return ODAPFormater(page)
        elif index == 1:
            return ExcelSplitPageV2(page)
        elif index == 2:
            return ODAPSearchValue(page)
        elif index == 3:
            return Email(page)
        else:
            raise ValueError("Unknown product type")
