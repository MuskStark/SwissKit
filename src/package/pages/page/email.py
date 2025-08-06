import re
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import flet as ft

from ...database.database_obj import DataBaseObj
from ...database.pojo.email_settings_config import EmailSettingConfig
from ...pages.toolbox_page import ToolBoxPage
from ...util.log_util import get_logger


class Email(ToolBoxPage):
    class Postman:
        def __init__(self, _email_config, _logger=get_logger(name='email')):
            self.logger = _logger
            self.email_config = _email_config
            # if _email_config is None, stop init PostMan
            self.sent_server = None
            # init status
            self.complete_init = False
            self.is_connected = False
            try:
                if self.email_config:
                    self.logger.info("开始初始化邮差")
                    if self.email_config.server_type == 'smtp':
                        if self.email_config.sent_active_ssl:
                            context = ssl.create_default_context()
                            self.sent_server = smtplib.SMTP_SSL(
                                self.email_config.sent_server_url,
                                self.email_config.sent_server_port,
                                timeout=30,
                                context=context
                            )
                        else:
                            self.sent_server = smtplib.SMTP(
                                self.email_config.sent_server_url,
                                self.email_config.sent_server_port,
                                timeout=30,
                            )
                        self.complete_init = True
                        self.logger.info('邮差初始化成功')
                else:
                    self.complete_init = False
                    self.logger.error("无配置文件，无法完成邮差初始化")
            except Exception as e:
                self.complete_init = False
                self.logger.error(f'邮差初始化异常：{e}')

        def _check_init_result(self) -> bool:
            self.logger.info('开始检查邮差是否完成初始化')
            if self.complete_init:
                self.logger.info('通过邮差初始化检查')
            else:
                self.logger.error('未通过邮差初始化检查')
            self.logger.info('完成邮差初始化检查')
            return self.complete_init

        def _connect_server(self):
            self.logger.info('开始与Email服务器建立连接')
            try:
                if not self.is_connected:
                    self.sent_server.login(self.email_config.user_name, self.email_config.password)
                    self.is_connected = True
                    self.logger.info('已成功建立连接')
            except Exception as e:
                self.logger.error(f'与Email服务器建立连接失败{e}')

        def _ensure_connection(self):
            if not hasattr(self, 'sent_server') or not self.is_connected:
                self._connect_server()
                return
            try:
                status = self.sent_server.noop()[0]
                if status != 250:
                    raise smtplib.SMTPException("Connection test failed")
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPException, AttributeError):
                self.logger.info("连接已断开，正在重新连接...")
                self.connection_active = False
                self._connect_server()

        def sent(self, _to, _cc_list, _subject, _body):
            self.logger.info('开始发送邮件')
            try:
                self._ensure_connection()
                message = MIMEMultipart()
                message['From'] = self.email_config.user_name
                message['To'] = ', '.join(_to)
                if _cc_list:
                    message['Cc'] = ', '.join(_cc_list)
                message['Subject'] = _subject
                message.attach(MIMEText(_body, 'plain'))
                all_recipients = _to + (_cc_list if _cc_list else [])
                self.sent_server.sendmail(self.email_config.user_name, all_recipients, message.as_string())
                self.logger.info('邮件发送成功')
            except Exception as e:
                self.logger.error(f'邮件发送失败{e}')
            pass

    def __init__(self, main_page: ft.Page):
        self.theme = {
            "text_color": ft.Colors.GREY_600
        }
        self.page = main_page
        self.database = DataBaseObj()
        self.logger = get_logger(name='email')

    def _setting_page(self) -> ft.Column:
        def on_dropdown_change(e, _server: ft.Row):
            _server_type_label = f'请输入{e.control.value}服务器地址'
            _server_port_label = f'请输入{e.control.value}服务端口'
            _server.controls[0].label = _server_type_label
            _server.controls[0].disabled = False
            _server.controls[1].label = _server_port_label
            _server.controls[1].disabled = False
            self.page.update()

        def _save_settings(_drop_down: ft.Dropdown, _server: ft.Row, _auth: ft.Row):
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

        config_list = None
        if not EmailSettingConfig.table_exists():
            self.database.creat_table([EmailSettingConfig])
        else:
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
                ft.dropdown.Option("pop3"),
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

    def _email_sent_page(self) -> ft.Column:
        config_list = list(EmailSettingConfig.select())
        if config_list:
            postman = self.Postman(_email_config=config_list[0], _logger=self.logger)

        to_text_filed = ft.TextField(label='请输入收件人')
        to_component = ft.Row(controls=[ft.Text('收件人'), to_text_filed], expand=True)
        cc_text_filed = ft.TextField(label='请输入抄送人')
        cc_component = ft.Row(controls=[ft.Text('抄送'), cc_text_filed], expand=True)
        content_text_fild = ft.TextField(label="邮件正文", multiline=True)

        sent_button = ft.ElevatedButton(text='发送',
                                        on_click=lambda _: postman.sent(to_text_filed.value, None, None, None))
        return ft.Column(
            controls=[to_component, cc_component, content_text_fild, sent_button],
            expand=True
        )

    def gui(self):
        def on_tab_change(_e, _tabs):
            if _e.control.selected_index == 0:
                _tabs.tabs[0].content = self._email_sent_page()
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
                        content=self._email_sent_page(),
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
