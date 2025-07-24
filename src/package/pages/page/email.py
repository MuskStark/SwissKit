import flet as ft

from ...database.pojo.email_settings_config import EmailSettingConfig
from ...pages.toolbox_page import ToolBoxPage
from ...database.database_obj import DataBaseObj
from ...util.log_util import get_logger


class Email(ToolBoxPage):
    def __init__(self, main_page: ft.Page):
        self.theme = {
            "text_color": ft.Colors.GREY_600
        }
        self.page = main_page
        self.database = DataBaseObj()
        self.logger = get_logger(name='email')

    def _setting_page(self) -> ft.Column:
        def on_dropdown_change(e, _server: ft.Row):
            server_type_label = f'请输入{e.control.value}服务器地址'
            server_port_label = f'请输入{e.control.value}服务端口'
            _server.controls[0].label = server_type_label
            _server.controls[0].disabled = False
            _server.controls[1].label = server_port_label
            _server.controls[1].disabled = False
            self.page.update()

        def _save_settings(_drop_down: ft.Dropdown, _server: ft.Row, _auth: ft.Row):
            self.logger.info('开始修改邮件设置')
            self.database.creat_table([EmailSettingConfig])
            # get all setting configs
            server_type = _drop_down.value
            server_url = _server.controls[0].value
            server_port = _server.controls[1].value
            ssl = _server.controls[2].value
            user_name = _auth.controls[0].value
            password = _auth.controls[1].value

            config = EmailSettingConfig.get_or_none(EmailSettingConfig.user_name == user_name)
            if config:
                config.server_type = server_type
                config.sent_server_url = server_url
                config.sent_server_port = server_port
                config.sent_active_ssl = ssl
                config.user_name = user_name
                config.password = password
            else:
                config = EmailSettingConfig(server_type=server_type,
                                            sent_server_url=server_url,
                                            sent_server_port=server_port,
                                            sent_active_ssl=ssl,
                                            user_name=user_name,
                                            password=password)
            config.save()

        drop_down = ft.Dropdown(
            label='选择验证模式',
            options=[
                ft.dropdown.Option("smtp"),
                ft.dropdown.Option("pop3"),
            ],
            on_change=lambda e: on_dropdown_change(e, server),
            width=200
        )
        server = ft.Row(controls=[ft.TextField(label='请先选择验证模式', disabled=True),
                                  ft.TextField(label='请先选择验证模式', disabled=True),
                                  ft.Checkbox(label="启用加密链接")], expand=True)
        auth = ft.Row(controls=[ft.TextField(label='请输入邮箱账号'),
                                ft.TextField(label='请输入密码', password=True, can_reveal_password=True)],expand=True)

        return ft.Column(
            controls=[
                drop_down,
                server,
                auth,
                ft.Row(controls=[ft.ElevatedButton(text='保存配置', on_click=lambda _:_save_settings(drop_down,server,auth))], alignment=ft.MainAxisAlignment.CENTER,
                       expand=True)
            ]
        )

    def gui(self):
        def on_tab_change(_e, _tabs):
            if _e.control.selected_index == 1:
                _tabs.tabs[1].content = self._setting_page()
                _tabs.update()
                _e.page.update()

        tab = ft.Tabs(
            on_change=lambda e: on_tab_change(e, tab),
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
