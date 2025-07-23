import flet as ft
from ...pages.toolbox_page import ToolBoxPage


class Email(ToolBoxPage):
    def __init__(self, main_page: ft.Page):
        self.theme = {
            "text_color": ft.Colors.GREY_600
        }
        self.page = main_page

    def gui(self):
        tab = ft.Tabs(
            tabs=[
                ft.Tab(
                    text='邮件发送',
                    content=ft.Container(
                        content=ft.Container(),
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text='邮件设置',
                    content=ft.Container(
                        content=ft.Container(),
                        padding=ft.padding.only(top=20),
                    ),
                )
            ]
        )
        return tab