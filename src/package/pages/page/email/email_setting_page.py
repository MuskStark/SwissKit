import re

import flet as ft

from ....database.pojo.email.email_settings_config import EmailSettingConfig


class EmailSetting:
    def __init__(self, page, logger, database_pojo):
        self.page = page
        self.logger = logger
        self.database = database_pojo

        # init ui component
        self.label = '请先选择验证模式'
        self.user_name_label = '请输入邮箱账号'
        self.password_label = '请输入密码'

        self.sent_server_url_value = None
        self.sent_server_port_value = None
        self.sent_active_ssl_value = False
        self.sent_active_tls_value = False
        self.user_name_value = None
        self.password_value = None

        self.drop_down = ft.Dropdown(label='选择验证模式',
                                     options=[ft.dropdown.Option("smtp"),  # ft.dropdown.Option("pop3"),
                                              ], on_change=lambda e: self._on_dropdown_change(e), width=200)

    def _create_ui_components(self):


        self.server_url_text = ft.TextField(label=self.label, value=self.sent_server_url_value, disabled=True)
        self.server_port_text = ft.TextField(label=self.label, value=self.sent_server_port_value, disabled=True)
        self.ssl_checkbox = ft.Checkbox(label="SSL", value=self.sent_active_ssl_value)
        self.tls_checkbox = ft.Checkbox(label="TLS", value=self.sent_active_tls_value)

        self.username_text = ft.TextField(label=self.user_name_label, value=self.user_name_value)
        self.password_text = ft.TextField(label=self.password_label, value=self.password_value, password=True,
                                          can_reveal_password=True)

    def _on_dropdown_change(self,e):
        server_type_label = f'请输入{e.control.value}服务器地址'
        server_port_label = f'请输入{e.control.value}服务端口'
        self.server_url_text.label = server_type_label
        self.server_url_text.disabled = False
        self.server_port_text.label = server_port_label
        self.server_port_text.disabled = False
        self.page.update()



    def setting_page(self) -> ft.Container:
        self.logger.info('开始初始化邮件配置界面')

        config_list = None
        self.logger.info('检查邮件配置数据表是否存在')
        if not EmailSettingConfig.table_exists():
            self.logger.info('数据表不存在，开始初始化数据表')
            self.database.creat_table([EmailSettingConfig])
        else:
            self.logger.info('存在数据表，开始邮件配置信息')
            config_list = list(EmailSettingConfig.select())

        # ui
        # GET CONFIG FROM DATABASE
        if config_list:
            self.label = '已生效配置'
            self.drop_down.value = config_list[0].server_type
            self.sent_server_url_value = config_list[0].sent_server_url
            self.sent_server_port_value = config_list[0].sent_server_port
            self.sent_active_ssl_value = config_list[0].sent_active_ssl
            self.sent_active_tls_value = config_list[0].sent_active_tls
            self.user_name_value = config_list[0].user_name
            self.password_value = config_list[0].password

        self._create_ui_components()

        server = ft.Column(controls=[ft.Row(controls=[self.server_url_text, self.server_port_text], expand=True),
                                     ft.Row(controls=[self.ssl_checkbox, self.tls_checkbox]),
                                     ], expand=True)

        auth = ft.Row(controls=[self.username_text, self.password_text], expand=True)



        self.logger.info('完成配置界面UI初始化')
        return ft.Container(content=ft.Column(controls=[self.drop_down, server, auth, ft.Row(
            controls=[ft.ElevatedButton(text='保存配置', on_click=lambda _: self._save_settings(self.drop_down))],
            alignment=ft.MainAxisAlignment.CENTER, expand=True)]), margin=ft.Margin(left=0, right=0, top=10, bottom=0))

    def _save_settings(self, _drop_down: ft.Dropdown):
        self.logger.info('开始邮件配置')
        dlg = ft.AlertDialog(title=ft.Text("通知"), content=ft.Text(""), alignment=ft.alignment.center,
                             title_padding=ft.padding.all(25), )
        self.page.add(dlg)
        try:
            self.logger.info('开始修改邮件设置')
            # get all setting configs
            server_type = _drop_down.value
            server_url = self.server_url_text.value
            server_port = self.server_port_text.value
            ssl = self.ssl_checkbox.value
            tls = self.tls_checkbox.value
            user_name = self.username_text.value
            password = self.password_text.value

            # valid config
            self.logger.info('开始验证配置合法性')
            url_pattern = re.compile(r'^(https?://)?'  # http 或 https 协议
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
                    config.sent_active_tls = tls
                    config.user_name = user_name
                    config.password = password
                else:
                    config = EmailSettingConfig(server_type=server_type, sent_server_url=server_url,
                                                sent_server_port=server_port, sent_active_ssl=ssl,
                                                sent_active_tls=tls,
                                                user_name=user_name, password=password)
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
