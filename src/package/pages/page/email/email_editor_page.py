import ast
from pathlib import Path

import flet as ft
from peewee import OperationalError

from ....components.file_or_path_picker import FileOrPathPicker
from ....components.multi_select_component import MultiSelectComponent
from ....components.progress_ring_components import ProgressRingComponent
from ....database.database_obj import DataBaseObj
from ....database.pojo.email.email_address import EmailAddressInfo
from ....database.pojo.email.email_group import EmailGroup
from ....database.pojo.email.email_settings_config import EmailSettingConfig
from ....enums.layout_enums import Layout
from ....enums.progress_status_enums import ProgressStatus
from ....util.postman import Postman


class EmailEditor:
    def __init__(self, page, logger, database_pojo: DataBaseObj):
        self.page = page
        self.logger = logger
        self.database = database_pojo

        self.progress_ring = ProgressRingComponent()

        # init dropdownOptions
        self.logger.info('开始加载分组信息')
        try:
            self.group_name_option = list(EmailGroup.select())
        except OperationalError as e:
            self.logger.info('缺少所需数据表，开始创建')
            self.database.creat_table([EmailGroup])
            self.logger.info('完成数据表创建')
            self.group_name_option = None
        if self.group_name_option is None:
            self.group_name_option = []
        else:
            self.group_name_option = [value.group_name for value in self.group_name_option]
        self.logger.info(f'完成分组信息加载:{self.group_name_option}')

    def email_sent_page(self) -> ft.Container:
        self.logger.info('开始初始化邮件发送界面')
        self.logger.info('开始查询邮件配置信息')

        to_text_field = MultiSelectComponent(dropdown_label='请选择收件人分组', options=self.group_name_option,
                                             layout=Layout.Horizontal)
        to_component = ft.Row(controls=[ft.Text('收件人'), to_text_field], expand=True)
        cc_text_field = MultiSelectComponent(dropdown_label='请选择抄送分组', options=self.group_name_option,
                                             layout=Layout.Horizontal)
        cc_component = ft.Row(controls=[ft.Text('抄送'), cc_text_field], expand=True)
        subject_text_field = ft.TextField(label="邮件标题", multiline=False)
        content_text_field = ft.TextField(label="邮件正文", multiline=True, height=200, expand=True)

        files = ft.Ref[ft.Column]()

        path_picker = FileOrPathPicker(self.page, ft.Icons.UPLOAD, False, '选择附件文件所在文件夹')
        split_separator = ft.TextField(label='请输入标签分隔符')
        check_box = ft.Checkbox(label='是否开启根据附件文件名中的标签进行批量发送',
                                on_change=lambda _: _on_checkbox_change())

        batch_file_folder = ft.Container(content=ft.Column(controls=[path_picker, split_separator], expand=True),
                                         disabled=True, expand=True)

        def _on_checkbox_change():
            if check_box.value:
                batch_file_folder.disabled = False
            else:
                batch_file_folder.disabled = True
            batch_file_folder.update()

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
            try:
                if EmailSettingConfig.table_exists():
                    config_list = list(EmailSettingConfig.select())
                    if config_list:
                        self.logger.info('使用邮件配置信息初始化邮差')
                        self.progress_ring.update_status(ProgressStatus.LOADING, '使用邮件配置信息初始化邮差')
                        postman = Postman(_email_config=config_list[0], _logger=self.logger)
                        to_tag_list = to_text_field.get_selected_values()
                        cc_tag_list = cc_text_field.get_selected_values()
                        to_list = []
                        cc_list = []
                        if check_box.value:
                            attachment_dic = {}
                            attachment_path = Path(path_picker.get_pick_value())
                            if attachment_path.exists() and attachment_path.is_dir():
                                all_file = [file.name for file in attachment_path.iterdir() if file.is_file()]
                                for file in all_file:
                                    if split_separator.value in Path(file).stem:
                                        file_name = Path(file).stem
                                        tag_from_file = file_name.rsplit(split_separator.value, 1)[-1]
                                        if tag_from_file in attachment_dic.keys():
                                            attachment_dic[tag_from_file].append(str(Path(attachment_path, file)))
                                        else:
                                            attachment_dic[tag_from_file] = [str(Path(attachment_path, file))]
                            if attachment_dic:
                                for tag, file_list in attachment_dic.items():
                                    att_to_list = []
                                    att_cc_list = []
                                    email_pojo_list = [addr for addr in list(
                                        EmailAddressInfo.select().where(EmailAddressInfo.email_tag.contains(tag)))]
                                    if to_tag_list or cc_tag_list:
                                        for email_pojo in email_pojo_list:
                                            if to_tag_list:
                                                for _to in to_tag_list:
                                                    if _to in ast.literal_eval(email_pojo.email_tag):
                                                        att_to_list.append(email_pojo.email_address)
                                            if cc_tag_list:
                                                for _cc in cc_tag_list:
                                                    if _cc in ast.literal_eval(email_pojo.email_tag):
                                                        att_cc_list.append(email_pojo.email_address)
                                    if len(att_to_list) == 0:
                                        att_to_list = [pojo.email_address for pojo in email_pojo_list]
                                    self.progress_ring.update_status(ProgressStatus.LOADING,
                                                                     f'正在发送邮件给{att_to_list}')
                                    postman.sent(att_to_list, att_cc_list, subject_text_field.value,
                                                 content_text_field.value, file_list)

                        else:
                            for to_tag in to_tag_list:
                                to_list.extend([addr.email_address for addr in list(
                                    EmailAddressInfo.select().where(EmailAddressInfo.email_tag.contains(to_tag)))])
                            for cc_tag in cc_tag_list:
                                cc_list.extend([addr.email_address for addr in list(
                                    EmailAddressInfo.select().where(EmailAddressInfo.email_tag.contains(cc_tag)))])
                            self.progress_ring.update_status(ProgressStatus.LOADING, f'正在发送邮件给{to_list}')
                            postman.sent(to_list, cc_list, subject_text_field.value,
                                         content_text_field.value, _get_attachments_list(files))
                        self.progress_ring.update_status(ProgressStatus.SUCCESS, f'完成邮件发送')
                    else:
                        self.progress_ring.update_status(ProgressStatus.ERROR, '无配置文件，无法初始化邮差')
                        self.logger.warning('无配置文件，无法初始化邮差')
                else:
                    self.progress_ring.update_status(ProgressStatus.ERROR, '无数据表，无法初始化邮差')
                    self.logger.error('无数据表，无法初始化邮差')
            except Exception as e:
                self.logger.error(e)
                self.progress_ring.update_status(ProgressStatus.ERROR, f'{e}')

        def _sent_email_async():
            import threading
            threading.Thread(target=_sent_email, daemon=True).start()

        sent_button = ft.ElevatedButton(text='发送', on_click=lambda _: _sent_email_async())
        self.logger.info('完成邮件发送界面UI初始化')
        return ft.Container(content=ft.Column(controls=[to_component, cc_component, subject_text_field,
                                                        ft.Container(content=ft.Column(controls=[content_text_field],
                                                                                       scroll=ft.ScrollMode.AUTO,
                                                                                       expand=True),
                                                                     height=200),
                                                        ft.ElevatedButton("选择附件", icon=ft.Icons.ATTACH_FILE,
                                                                          on_click=lambda _: file_picker.pick_files(
                                                                              allow_multiple=True), ),
                                                        ft.Column(ref=files),
                                                        check_box,
                                                        batch_file_folder,
                                                        ft.Row(controls=[sent_button],
                                                               alignment=ft.MainAxisAlignment.CENTER,
                                                               expand=True),
                                                        self.progress_ring
                                                        ],
                                              expand=True),
                            margin=ft.Margin(left=0, right=0, top=10, bottom=0)
                            )
