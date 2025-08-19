import ast

import flet as ft

from ....database.pojo.email.email_address import EmailAddressInfo
from ....database.pojo.email.email_group import EmailGroup


class EmailInfo:
    def __init__(self, page, logger, database_pojo):
        self.page = page
        self.logger = logger
        self.database = database_pojo

    def email_group_page(self) -> ft.Container:
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
