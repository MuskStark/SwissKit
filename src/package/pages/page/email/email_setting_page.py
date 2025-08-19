import re

import flet as ft

from ....database.pojo.email.email_settings_config import EmailSettingConfig


class EmailSetting:
    def __init__(self, page, logger, database_pojo):
        self.page = page
        self.logger = logger
        self.database = database_pojo

    def setting_page(self) -> ft.Column:
        self.logger.info('开始初始化邮件配置界面')

        def on_dropdown_change(e, _server: ft.Row):
            _server_type_label = f'请输入{e.control.value}服务器地址'
            _server_port_label = f'请输入{e.control.value}服务端口'
            _server.controls[0].label = _server_type_label
            _server.controls[0].disabled = False
            _server.controls[1].label = _server_port_label
            _server.controls[1].disabled = False
            self.page.update()

        def _save_settings(_drop_down: ft.Dropdown, _server: ft.Row, _auth: ft.Row):
            self.logger.info('开始邮件配置')
            dlg = ft.AlertDialog(
                title=ft.Text("通知"),
                content=ft.Text(""),
                alignment=ft.alignment.center,
                title_padding=ft.padding.all(25),
            )
            self.page.add(dlg)
            try:
                self.logger.info('开始修改邮件设置')
                # get all setting configs
                server_type = _drop_down.value
                server_url = _server.controls[0].value
                server_port = _server.controls[1].value
                ssl = _server.controls[2].value
                user_name = _auth.controls[0].value
                password = _auth.controls[1].value

                # valid config
                self.logger.info('开始验证配置合法性')
                url_pattern = re.compile(
                    r'^(https?://)?'  # http 或 https 协议
                    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # 域名
                    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # 顶级域名
                    r'localhost|'  # 本地主机
                    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP 地址
                    r'(?::\d+)?'  # 端口号
                    r'(?:/?|[/?]\S+)$', re.IGNORECASE)  # 路径和查询参数
                is_url = re.match(url_pattern, server_url)
                is_port = 65535 >= 0 <= int(server_port)

                if is_url and is_port:
                    self.logger.info('已验证配置合法性')
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
                    self.logger.info('配置保存成功')
                    self.page.dialog = dlg
                    dlg.content.value = '配置保存成功'
                    dlg.open = True
                    self.page.update()
                else:
                    raise RuntimeError('配置合法性验证失败')
            except Exception as e:
                self.page.dialog = dlg
                dlg.content.value = '配置保存失败，请查看系统日志'
                dlg.open = True
                self.page.update()
                self.logger.error(f'配置保存错误{e}', exc_info=True)
            finally:
                self.logger.info('完成邮件配置')

        config_list = None
        self.logger.info('检查邮件配置数据表是否存在')
        if not EmailSettingConfig.table_exists():
            self.logger.info('数据表不存在，开始初始化数据表')
            self.database.creat_table([EmailSettingConfig])
        else:
            self.logger.info('存在数据表，开始邮件配置信息')
            config_list = list(EmailSettingConfig.select())

        _label = '请先选择验证模式'
        user_name_label = '请输入邮箱账号'
        password_label = '请输入密码'

        sent_server_url_value = None
        sent_server_port_value = None
        sent_active_ssl_value = False
        user_name_value = None
        password_value = None

        drop_down = ft.Dropdown(
            label='选择验证模式',
            options=[
                ft.dropdown.Option("smtp"),
                # ft.dropdown.Option("pop3"),
            ],
            on_change=lambda e: on_dropdown_change(e, server),
            width=200
        )
        # GET CONFIG FROM DATABASE
        if config_list:
            _label = '已生效配置'
            drop_down.value = config_list[0].server_type
            sent_server_url_value = config_list[0].sent_server_url
            sent_server_port_value = config_list[0].sent_server_port
            sent_active_ssl_value = config_list[0].sent_active_ssl
            user_name_value = config_list[0].user_name
            password_value = config_list[0].password
        server = ft.Row(controls=[ft.TextField(label=_label, value=sent_server_url_value, disabled=True),
                                  ft.TextField(label=_label, value=sent_server_port_value, disabled=True),
                                  ft.Checkbox(label="启用加密链接", value=sent_active_ssl_value)], expand=True)
        auth = ft.Row(controls=[ft.TextField(label=user_name_label, value=user_name_value),
                                ft.TextField(label=password_label, value=password_value, password=True,
                                             can_reveal_password=True)], expand=True)
        self.logger.info('完成配置界面UI初始化')
        return ft.Column(
            controls=[
                drop_down,
                server,
                auth,
                ft.Row(controls=[
                    ft.ElevatedButton(text='保存配置', on_click=lambda _: _save_settings(drop_down, server, auth))],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True)
            ]
        )
