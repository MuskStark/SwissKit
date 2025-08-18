import ast
import re

import flet as ft

from ...database.database_obj import DataBaseObj
from ...database.pojo.email.email_address import EmailAddressInfo
from ...database.pojo.email.email_group import EmailGroup
from ...database.pojo.email.email_settings_config import EmailSettingConfig
from ...pages.toolbox_page import ToolBoxPage
from ...util.log_util import get_logger
from ...util.postman import Postman


class Email(ToolBoxPage):

    def __init__(self, main_page: ft.Page):
        self.theme = {
            "text_color": ft.Colors.GREY_600
        }
        self.page = main_page
        self.database = DataBaseObj()
        self.logger = get_logger(name='email')

    def _setting_page(self) -> ft.Column:
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

    def _email_sent_page(self) -> ft.Column:
        self.logger.info('开始初始化邮件发送界面')
        self.logger.info('开始查询邮件配置信息')

        to_text_field = ft.TextField(label='请输入收件人')
        to_component = ft.Row(controls=[ft.Text('收件人'), to_text_field], expand=True)
        cc_text_field = ft.TextField(label='请输入抄送人')
        cc_component = ft.Row(controls=[ft.Text('抄送'), cc_text_field], expand=True)
        subject_text_field = ft.TextField(label="邮件标题", multiline=False)
        content_text_field = ft.TextField(label="邮件正文", multiline=True)

        files = ft.Ref[ft.Column]()

        def _file_picker_result(e: ft.FilePickerResultEvent):
            files.current.controls.clear()
            if e.files is not None:
                for f in e.files:
                    files.current.controls.append(ft.Row([ft.Text(f.path)]))
            self.page.update()

        file_picker = ft.FilePicker(on_result=_file_picker_result)
        self.page.overlay.append(file_picker)

        def _get_addr_list(_cc_text_file: ft.TextField):
            cc = _cc_text_file.value
            if not cc:
                return []

            if ';' in cc:
                return [item.strip() for item in cc.split(';') if item.strip()]
            else:
                return [cc.strip()] if cc.strip() else []

        def _get_attachments_list(_files: ft.Ref[ft.Column]):
            column_widget = _files.current
            files_path_list = []
            for control in column_widget.controls:
                if isinstance(control, ft.Text):
                    files_path_list.append(control.value)
            return files_path_list

        def _sent_email():
            if EmailSettingConfig.table_exists():
                config_list = list(EmailSettingConfig.select())
                if config_list:
                    self.logger.info('使用邮件配置信息初始化邮差')
                    postman = Postman(_email_config=config_list[0], _logger=self.logger)
                    postman.sent(_get_addr_list(to_text_field),
                                 _get_addr_list(cc_text_field),
                                 subject_text_field.value,
                                 content_text_field.value,
                                 _get_attachments_list(files))
                else:
                    self.logger.warning('无配置文件，无法初始化邮差')
            else:
                self.logger.error('无数据表，无法初始化邮差')

        sent_button = ft.ElevatedButton(text='发送',
                                        on_click=lambda _: _sent_email())
        self.logger.info('完成邮件发送界面UI初始化')
        return ft.Column(
            controls=[to_component, cc_component, subject_text_field, content_text_field,
                      ft.ElevatedButton(
                          "选择附件",
                          icon=ft.Icons.ATTACH_FILE,
                          on_click=lambda _: file_picker.pick_files(allow_multiple=True),
                      ),
                      ft.Column(ref=files),
                      sent_button],
            expand=True
        )

    def _email_group_page(self) -> ft.Container:
        # function area
        # Update Email Table
        def _update_data_table(_table: ft.DataTable):
            """
            Update the data table with email address information from the database.

            Summary:
            This function updates a given DataTable with email address and tag information
            retrieved from the database. It logs the start and completion of the update process.
            The function queries the database for email addresses, creates a list of rows,
            and assigns these to the provided DataTable. The page is then refreshed to reflect
            the changes.

            Args:
                _table (ft.DataTable): The DataTable to be updated with email address information.

            Raises:
                Any exceptions that may occur during the database operation or while updating
                the table will propagate up to the caller.

            Returns:
                None
            """
            # load data from database
            self.logger.info('开始更新邮件地址分组信息表')
            self.database.creat_table([EmailAddressInfo])
            address_list = list(EmailAddressInfo.select())
            table_row_list = []
            if address_list:
                for addr in address_list:
                    table_row_list.append(ft.DataRow(
                        [ft.DataCell(ft.Text(addr.email_address)),
                         ft.DataCell(ft.Text(addr.email_tag))],
                        on_select_changed=(lambda _addr:
                                           lambda e: _modify_email_address_info(_get_dlg(), '维护邮件地址信息',
                                                                                _old_addr=_addr.email_address,
                                                                                _old_tags=_addr.email_tag)
                                           )(addr),
                    ))
            else:
                table_row_list = None
            _table.rows = table_row_list
            self.page.update()
            self.logger.info('完成邮件地址分组信息表更新')

        def _update_group_data_table(_table: ft.DataTable):
            # load data from database
            self.logger.info('开始更新邮件分组信息表')
            self.database.creat_table([EmailGroup])
            group_list = list(EmailGroup.select())
            group_table_row_list = []
            if group_list:
                for group in group_list:
                    group_table_row_list.append(ft.DataRow(
                        [ft.DataCell(ft.Text(group.group_name))],
                        on_select_changed=(lambda _group:
                                           lambda e: _delete_group_info(_group.group_name)
                                           )(group),
                    ))
            else:
                group_table_row_list = None
            _table.rows = group_table_row_list
            self.page.update()
            self.logger.info('完成邮件分组信息表更新')

        def _modify_email_address_info(_dlg, _dil_title: str = None, _old_addr: str = None, _old_tags: str = None):
            """
            Modifies the email address information in a dialog, allowing for the addition and removal of tags associated with an email address.

            Summary:
            This function updates the title of the provided dialog, initializes a text field for email input, and sets up a row for displaying tags. It also defines internal functions to update the tag display, remove items from the tag list, handle dropdown changes, and modify the email address information in the database. The UI components, including a dropdown for selecting groups and a save button, are then added to the dialog, which is opened for user interaction.

            Parameters:
            - _dlg: Dialog
              The dialog object to be modified and displayed.
            - _dil_title: str, optional
              The title to set for the dialog. Defaults to None.

            Raises:
            - None

            Returns:
            - None
            """
            self.logger.info('开始维护邮件分组信息')
            _dlg.title.value = _dil_title
            tag_list = []
            if _old_tags:
                tag_list = ast.literal_eval(_old_tags)
            tag_display = ft.Row(wrap=True)
            address = ft.TextField(label='请输入邮件地址')
            if _old_addr:
                address.value = _old_addr

            def _update_tag_display():
                tag_display.controls.clear()
                for item in tag_list:
                    chip = ft.Container(
                        content=ft.Row([
                            ft.Text(item, size=14),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=16,
                                on_click=lambda e, item=item: _remove_item(item),
                                tooltip="删除"
                            )
                        ], tight=True),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=ft.Colors.BLUE_100,
                        border_radius=16,
                        margin=ft.margin.only(right=4, bottom=4)
                    )
                    tag_display.controls.append(chip)
                if hasattr(self, 'page') and self.page and _dlg.open:
                    tag_display.update()

            def _remove_item(item):
                if item in tag_list:
                    tag_list.remove(item)
                    _update_tag_display()

            def _tag_dropdown_changed(e):
                if e.control.value and e.control.value not in tag_list:
                    tag_list.append(e.control.value)
                    _update_tag_display()
                e.control.value = None  # 重置选择
                e.control.update()

            def _modify_email_address():
                self.logger.info('初始化邮件分组信息数据表')
                self.database.creat_table([EmailAddressInfo])
                info = EmailAddressInfo.get_or_none(EmailAddressInfo.email_address == address.value)
                if info is None:
                    info = EmailAddressInfo()
                if tag_list:
                    info.email_tag = str(tag_list)
                if address.value:
                    info.email_address = address.value
                info.save()
                self.logger.info('完成分组信息数据维护')

            # dlg ui
            # options query from database
            dropdown_options = None
            if not EmailGroup.table_exists():
                self.database.creat_table([EmailGroup])
            else:
                group_options = []
                group_list = list(EmailGroup.select())
                for group in group_list:
                    group_options.append(group.group_name)
                dropdown_options = [ft.DropdownOption(value) for value in group_options]

            group_dropdown = ft.Dropdown(
                label="选择分组",
                options=dropdown_options,
                on_change=_tag_dropdown_changed,
                width=300
            )
            save_bt = ft.ElevatedButton('新增', on_click=lambda _: _modify_email_address())
            content = ft.Column(controls=[address,
                                          ft.Row(controls=[group_dropdown, tag_display], expand=True),
                                          save_bt

                                          ])
            self.page.dialog = _dlg
            _dlg.content.content = content
            _dlg.open = True
            self.page.update()
            if tag_list:
                _update_tag_display()

        def _delete_group_info(_group_name):
            EmailGroup.delete().where(EmailGroup.group_name == _group_name).execute()
            _update_group_data_table(group_table)

        def _modify_group_info(_dlg, _dil_title: str = None):
            # function area
            def _modify_info():
                self.logger.info('开始检查是否有重名分组')
                value = EmailGroup.get_or_none(EmailGroup.group_name == group_name.value)
                if value is None:
                    self.logger.info('不存在重复分组信息，开始写入分组信息')
                    EmailGroup.create(group_name=group_name.value).save()
                    self.logger.info(f'完成分组写入{group_name.value}')
                else:
                    self.logger.warning('已存在分组信息')

            # ui code
            group_name = ft.TextField(label='请输入分组名称')
            group_modify_bt = ft.ElevatedButton('维护分组', on_click=lambda _: _modify_info())

            content = ft.Container(content=
                                   ft.Column(controls=[group_name, group_modify_bt])
                                   )
            # update _dlg ui
            _dlg.content.content = content
            _dlg.title = _dil_title
            _dlg.open = True
            self.page.update()

        #  dlg page
        self.logger.info('开始初始化邮件分组界面')

        def _get_dlg():
            dlg = ft.AlertDialog(
                title=ft.Text(),
                content=ft.Container(),
                alignment=ft.alignment.center,
                title_padding=ft.padding.all(25),
                on_dismiss=lambda _: _update_data_table(table)
            )
            self.page.add(dlg)
            return dlg \
 \
                # page ui code

        email_address_bt = ft.ElevatedButton('维护邮件地址',
                                             on_click=lambda _: _modify_email_address_info(_get_dlg(), '邮件地址维护'))
        group_info_bt = ft.ElevatedButton('维护分组信息',
                                          on_click=lambda _: _modify_group_info(_get_dlg(), '分组信息维护'))
        table = ft.DataTable(
            width=700,
            border=ft.border.all(2, ft.Colors.GREY_300),
            border_radius=4,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            heading_row_height=100,
            data_row_color={ft.ControlState.HOVERED: "0x30FF0000"},
            divider_thickness=0,
            column_spacing=200,
            columns=[
                ft.DataColumn(
                    ft.Text("邮件地址"),
                ),
                ft.DataColumn(
                    ft.Text("分组"),
                ),
            ],
            rows=None,
        )
        group_table = ft.DataTable(
            width=700,
            border=ft.border.all(2, ft.Colors.GREY_300),
            border_radius=4,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            heading_row_height=100,
            data_row_color={ft.ControlState.HOVERED: "0x30FF0000"},
            divider_thickness=0,
            column_spacing=200,
            columns=[
                ft.DataColumn(
                    ft.Text("邮件分组"),
                )
            ],
            rows=None,
        )
        _update_data_table(table)
        _update_group_data_table(group_table)
        self.logger.info('完成初始化邮件分组界面UI')
        return ft.Container(
            content=ft.Column(
                controls=[ft.Row(controls=[email_address_bt, group_info_bt], spacing=15, expand=True),
                          ft.Container(content=ft.Column(controls=[table], scroll=ft.ScrollMode.AUTO), height=200),
                          ft.Container(content=ft.Column(controls=[group_table], scroll=ft.ScrollMode.AUTO),
                                       height=200),
                          ],
                expand=True),
            margin=ft.Margin(left=0, right=0, top=20, bottom=0)
        )

    def gui(self):
        def on_tab_change(_e, _tabs):
            if _e.control.selected_index == 0:
                _tabs.tabs[0].content = self._email_sent_page()
            if _e.control.selected_index == 1:
                _tabs.tabs[1].content = self._email_group_page()
            if _e.control.selected_index == 2:
                _tabs.tabs[2].content = self._setting_page()
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
