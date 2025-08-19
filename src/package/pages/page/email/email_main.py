import flet as ft

from .email_info_page import EmailInfo
from .email_setting_page import EmailSetting
from ...toolbox_page import ToolBoxPage
from ....database.database_obj import DataBaseObj
from ....pages.page.email.email_editor_page import EmailEditor
from ....util.log_util import get_logger


class Email(ToolBoxPage):

    def __init__(self, main_page: ft.Page):
        self.theme = {
            "text_color": ft.Colors.GREY_600
        }
        self.page = main_page
        self.database = DataBaseObj()
        self.logger = get_logger(name='email')
        self.email_editor = EmailEditor(self.page, self.logger, self.database)
        self.email_setting = EmailSetting(self.page, self.logger, self.database)
        self.email_info = EmailInfo(self.page, self.logger, self.database)

    def gui(self):
        def on_tab_change(_e, _tabs):
            if _e.control.selected_index == 0:
                _tabs.tabs[0].content = self.email_editor.email_sent_page()
            if _e.control.selected_index == 1:
                _tabs.tabs[1].content = self.email_info.email_group_page()
            if _e.control.selected_index == 2:
                _tabs.tabs[2].content = self.email_setting.setting_page()
            _tabs.update()
            _e.page.update()

        tab = ft.Tabs(
            on_change=lambda e: on_tab_change(e, tab),
            tabs=[
                ft.Tab(
                    text='邮件发送',
                    content=ft.Container(
                        content=self.email_editor.email_sent_page(),
                        padding=ft.padding.only(top=20),
                    ),
                ),
                ft.Tab(
                    text='邮件分组设置',
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
                ),
            ]
        )
        return tab
