import ast

import flet as ft

from ....components.multi_select_component import MultiSelectComponent
from ....database.pojo.email.email_address import EmailAddressInfo
from ....database.pojo.email.email_group import EmailGroup


class EmailInfo:
    def __init__(self, page, logger, database_pojo):
        self.page = page
        self.logger = logger
        self.database = database_pojo

        # init database table
        self.database.creat_table([EmailAddressInfo, EmailGroup])

        self.email_address_table = ft.DataTable(
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

        self.group_info_table = ft.DataTable(
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

    # page ui

    def email_info_page(self)-> ft.Container:
        self.logger.info('开始初始化邮件分组界面')

        # button
        email_address_bt = ft.ElevatedButton('维护邮件地址',on_click= lambda _: self._open_email_address_modify_alg())
        group_info_bt = ft.ElevatedButton('维护分组信息',
                                          on_click=lambda _: self._open_group_modify_alg())
        self._load_table_data()



        return ft.Container(
            content=
            ft.Column(controls=[
                ft.Column(controls=[email_address_bt, ft.Container(content=ft.Column(controls=[self.email_address_table], scroll=ft.ScrollMode.AUTO), height=200),]),
                ft.Column(controls=[group_info_bt, ft.Container(content=ft.Column(controls=[self.group_info_table], scroll=ft.ScrollMode.AUTO),
                     height=200)])
            ],
                spacing=10,
                expand=True
            )
        )

    # load table data
    def _load_table_data(self):
        # load email address info
        self.logger.info('开始更新邮件地址信息表')
        address_list = list(EmailAddressInfo.select())
        email_address_table_row_list = []
        if address_list:
            for addr in address_list:
                email_address_table_row_list.append(ft.DataRow(
                    [ft.DataCell(ft.Text(addr.email_address)),
                     ft.DataCell(ft.Text(addr.email_tag))],
                    on_select_changed=(lambda _addr:
                                       lambda e: self._open_email_address_modify_alg(
                                           model=1,
                                           old_email_address=_addr.email_address,
                                           old_tags=ast.literal_eval(_addr.email_tag))
                                       )(addr),
                ))
        else:
            email_address_table_row_list = None
        self.email_address_table.rows = email_address_table_row_list

        # load group info
        self.logger.info('开始更新邮件分组信息表')
        self.database.creat_table([EmailGroup])
        group_list = list(EmailGroup.select())
        group_table_row_list = []
        if group_list:
            for group in group_list:
                group_table_row_list.append(ft.DataRow(
                    [ft.DataCell(ft.Text(group.group_name))],
                    on_select_changed=(lambda _group:
                                       lambda e: self._delete_group_info(_group.group_name)
                                       )(group),
                ))
        else:
            group_table_row_list = None
        self.group_info_table.rows = group_table_row_list

    # dlg component
    def _get_dlg(self, dlg_title:str):
        self.logger.info('开始初始化弹窗')
        dlg = ft.AlertDialog(
            title=ft.Text(dlg_title),
            content=ft.Container(),
            alignment=ft.alignment.center,
            title_padding=ft.padding.all(25),
            on_dismiss=lambda _: self._update_info_page()
        )
        self.page.add(dlg)
        self.logger.info('完成弹窗初始化')
        return dlg

    # update page
    def _update_info_page(self):
        self._load_table_data()
        self.page.update()

    # email_group_info function

    def _open_group_modify_alg(self):
        # generate dlg ui
        dlg = self._get_dlg('新增邮件分组标签')
        group_name = ft.TextField(label='请输入分组名称')
        group_modify_bt = ft.ElevatedButton('维护分组', on_click=lambda _: _modify_info())

        content = ft.Container(content=
                               ft.Column(controls=[group_name, group_modify_bt])
                               )
        dlg.content.content = content
        dlg.open = True
        self.page.update()

        def _modify_info():
            self.logger.info('开始检查是否有重名分组')
            value = EmailGroup.get_or_none(EmailGroup.group_name == group_name.value)
            if value is None:
                self.logger.info('不存在重复分组信息，开始写入分组信息')
                EmailGroup.create(group_name=group_name.value).save()
                self.logger.info(f'完成分组写入{group_name.value}')
            else:
                self.logger.warning('已存在分组信息')
            dlg.open = False
                # update email info page

    def _delete_group_info(self,group_name:str):
        self.logger.info(f'开始删除{group_name}')
        EmailGroup.delete().where(EmailGroup.group_name == group_name).execute()
        # delete tag from email address tab
        self.logger.info(f'开始同步删除Email_Address表中涉及{group_name}的数据')
        email_address = EmailAddressInfo.select()
        if email_address:
            for email in email_address:
                tag_list = ast.literal_eval(email.email_tag)
                if group_name in tag_list:
                    self.logger.info(f'{email.email_address}涉及{group_name}标签，开始清理')
                    tag_list.remove(group_name)
                    email.email_tag = str(tag_list)
                    email.save()
                    self.logger.info(f'{email.email_address}完成清理，最新标签为{email.email_tag}')
            self.logger.info(f'Email_Address表中无数据涉及{group_name}的数据')
        else:
            self.logger.info(f'Email_Address表中无数据, 无需清理')
        self._update_info_page()
        self.logger.info(f'删除{group_name}结束')

    def _update_group_data_table(self, table: ft.DataTable):
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
                                       lambda e: self._delete_group_info(_group.group_name)
                                       )(group),
                ))
        else:
            group_table_row_list = None
        table.rows = group_table_row_list
        self.page.update()
        self.logger.info('完成邮件分组信息表更新')


    # email_address function
    def _open_email_address_modify_alg(self, model:int=0, old_email_address:str=None, old_tags:list[str]=None):
        if model == 0:
            dlg_title = '新增邮件地址信息'
        else:
            dlg_title = '维护邮件地址信息'
        dlg = self._get_dlg(dlg_title)

        # dlg ui
        group_options = []
        group_list = list(EmailGroup.select())
        for group in group_list:
            group_options.append(group.group_name)
        if old_tags:
            email_tag_multi_selector = MultiSelectComponent('请选择分组', options=group_options, tag_list=old_tags)
        else:
            email_tag_multi_selector = MultiSelectComponent('请选择分组', options=group_options)
        address = ft.TextField(label='请输入邮件地址')
        if old_email_address:
            address.value = old_email_address

        save_bt = ft.ElevatedButton('维护', on_click=lambda _: _modify_email_info())

        content = ft.Column(controls=[address,email_tag_multi_selector,save_bt])

        dlg.content.content = content
        dlg.open = True
        self.page.update()
        # dlg function
        def _modify_email_info():
            if model != 0:
                info = EmailAddressInfo.get_or_none(EmailAddressInfo.email_address == old_email_address)
            else:
                info = EmailAddressInfo()
            if info:
                info.email_address = address.value
                info.email_tag = str(email_tag_multi_selector.get_selected_values())
                info.save()
