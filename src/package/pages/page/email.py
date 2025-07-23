import flet as ft

from ...pages.toolbox_page import ToolBoxPage


class Email(ToolBoxPage):
    def __init__(self, main_page: ft.Page):
        self.theme = {
            "text_color": ft.Colors.GREY_600
        }
        self.page = main_page

    def _setting_page(self) -> ft.Column:
        def on_dropdown_change(e,_server: ft.Row):
            server_type_label = f'请输入{e.control.value}服务器地址'
            server_port_label = f'请输入{e.control.value}服务端口'
            _server.controls[0].label = server_type_label
            _server.controls[0].disabled = False
            _server.controls[1].label = server_type_label
            _server.controls[1].disabled = False
            self.page.update()

        drop_down = ft.Dropdown(
            label='选择验证模式',
            options=[
                ft.dropdown.Option("smtp"),
                ft.dropdown.Option("pop3"),
            ],
            on_change= lambda e:on_dropdown_change(e, server),
            width=200
        )
        server = ft.Row(controls=[ft.TextField(label='请先选择验证模式', disabled=True),ft.TextField(label='请先选择验证模式', disabled=True)])
        auth = ft.Row(controls=[ft.TextField(label='请输入邮箱账号'), ft.TextField(label='请输入密码', password=True, can_reveal_password=True)])

        return ft.Column(
            controls=[
                drop_down,
                server,
                auth,
                ft.Row(controls=[ft.ElevatedButton(text='保存配置')],alignment=ft.MainAxisAlignment.CENTER,expand=True)
            ]
        )





    def gui(self):
        def on_tab_change(_e, _tabs):
            if _e.control.selected_index == 1:
                _tabs.tabs[1].content = self._setting_page()
                _tabs.update()
                _e.page.update()
        tab = ft.Tabs(
            on_change= lambda e:on_tab_change(e, tab),
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