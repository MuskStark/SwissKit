from asyncio import sleep
from pathlib import Path

import flet as ft
import pandas as pd

from ...components.progress_ring_components import ProgressRingComponent
from ...enums.progress_status_enums import ProgressStatus
from ...pages.toolbox_page import ToolBoxPage


class ODAPSearchValue(ToolBoxPage):
    def __init__(self, main_page: ft.Page):
        self.theme = {
            "text_color": ft.Colors.GREY_600
        }
        self.file_analyze_dic = {}
        self.page = main_page
        self.disable = False

    def _picker(self, e: ft.FilePickerResultEvent,
                file_path_text: ft.TextField,
                progress: ft.ProgressRing = None,
                icon_success: ft.Icon = None,
                icon_error: ft.Icon = None,
                info_text: ft.Text = None,
                is_file: bool = True):
        if is_file:
            if e.files:
                if Path(e.files[0].path).suffix.lower() not in ['.xlsx']:
                    file_path_text.value = ''
                    file_path_text.error_text = '请上传xlsx文件'
                    file_path_text.update()
                else:
                    file_path_text.value = e.files[0].path
                    file_path_text.error_text = ''
                    file_path_text.update()
        else:
            if e.path:
                file_path_text.value = e.path
        if progress is not None:
            progress.visible = False
        if icon_success is not None:
            icon_success.visible = False
        if icon_error is not None:
            icon_error.visible = False
        if info_text is not None:
            info_text.visible = False
        self.page.update()

    def file_analyze(self, file_path_text: ft.TextField,
                     progress: ft.ProgressRing,
                     icon_success: ft.Icon,
                     icon_error: ft.Icon,
                     info_text: ft.Text,
                     sheet_selector: ft.Dropdown,
                     columns_selector: ft.Dropdown,
                     ):
        try:
            if sheet_selector.value is not None:
                sheet_selector.value = None
                sheet_selector.visible = False
                sheet_selector.update()
                sheet_selector.visible = True
                self.page.update()
            if columns_selector.value is not None:
                columns_selector.value = None
                columns_selector.visible = False
                columns_selector.update()
                columns_selector.visible = True
                self.page.update()

            self.file_analyze_dic = {}
            if file_path_text.value:
                # 读取 Excel 文件
                icon_error.visible = False
                progress.visible = True
                info_text.visible = True
                self.page.update()
                excel_file = pd.ExcelFile(file_path_text.value)
                # 获取所有 sheet 的名称
                sheet_names = excel_file.sheet_names
                # 遍历每个 sheet，读取表头
                for sheet_name in sheet_names:
                    # 读取当前 sheet 的第一行作为表头
                    df = excel_file.parse(sheet_name, nrows=1)
                    headers = df.columns.tolist()
                    self.file_analyze_dic[sheet_name] = headers
                if self.file_analyze_dic.keys():
                    progress.visible = False
                    icon_success.visible = True
                    info_text.value = '解析成功'
                    sheet_selector.options = [ft.dropdown.Option(value) for value in list(self.file_analyze_dic.keys())]
                    self.page.update()
            else:
                raise RuntimeError('未选择数据源')
        except Exception as e:
            progress.visible = False
            icon_success.visible = False
            icon_error.visible = True
            # 强制更新text组件
            info_text.visible = False
            info_text.value = str(e)
            info_text.update()
            info_text.visible = True
            self.page.update()

    def sheet_dropdown_changed(self, selector: ft.Dropdown, columns_selector: ft.Dropdown):
        if columns_selector.value is not None:
            columns_selector.value = None
            columns_selector.visible = False
            columns_selector.update()
            columns_selector.visible = True
        columns_selector.options = [ft.DropdownOption(value) for value in self.file_analyze_dic[selector.value]]
        columns_selector.update()
        self.page.update()

    def clear_dropdown(self, selector: ft.Dropdown, columns_selector: ft.Dropdown):
        columns_selector.value = None
        columns_selector.options = None
        selector.value = None
        selector.options = None
        self.page.update()

    def gui(self):
        # 文件选择组件
        file_picker = ft.FilePicker(
            on_result=lambda e: self._picker(e, file_path_text, progress, finished_icon, error_icon, info_text))
        file_path_text = ft.TextField(label='请选择数据源文件(.xlsx)', expand=True)
        picker_components = ft.Row(
            [ft.IconButton(
                icon=ft.Icons.UPLOAD_FILE,
                on_click=lambda _: file_picker.pick_files()
            ),
                file_path_text
            ])
        # 1.1列拆分功能
        sheet_selector = ft.Dropdown(
            label='请选择Sheet页',
            on_change=lambda _: self.sheet_dropdown_changed(sheet_selector, columns_selector),
            options=[],
            width=200,
            disabled=self.disable,
        )
        columns_selector = ft.Dropdown(
            label='请选择需数据列',
            options=[],
            width=300,
            disabled=self.disable,
        )
        # 1.2文件解析按钮组件
        progress = ft.ProgressRing(visible=False)
        finished_icon = ft.Icon(ft.Icons.DONE, color="green", visible=False)
        error_icon = ft.Icon(ft.Icons.ERROR, color="red", visible=False)
        info_text = ft.Text(value='开始解析文件', visible=False)
        progress_components = ft.Row([ft.Row(controls=[progress, finished_icon, error_icon], spacing=0), info_text])
        analyze_button = ft.ElevatedButton(text='文件分析',
                                           on_click=lambda _: self.file_analyze(file_path_text,
                                                                                progress,
                                                                                finished_icon,
                                                                                error_icon,
                                                                                info_text,
                                                                                sheet_selector,
                                                                                columns_selector)
                                           , disabled=self.disable
                                           )
        analyze = ft.Column([ft.Row(alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        analyze_button,
                                        progress_components, ]),
                             ft.Row([sheet_selector, columns_selector], alignment=ft.MainAxisAlignment.CENTER,
                                    expand=True)
                             ], expand=True, spacing=15)

        # 处理进度条
        handel_progress = ProgressRingComponent()

        self.page.overlay.extend([file_picker])

        # MarkDown组件
        markdown = ft.Markdown(
            extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,  # 使用GitHub扩展语法
            code_theme=ft.MarkdownCodeTheme.GOOGLE_CODE,  # 接近GitHub的语法高亮主题
            selectable=True,  # 允许代码选择
        )

        markdown_area = ft.Container(
            ft.Column([markdown],scroll=ft.ScrollMode.AUTO),
            border=ft.border.all(1, "#e1e4e8"),  # GitHub风格边框颜色
            border_radius=6,  # 圆角大小
            padding=10,
            bgcolor="#f6f8fa",# GitHub代码块背景色
            height=200,
            visible=False

        )

        return ft.Column(
            controls=[
                ft.Column(
                    controls=[picker_components],
                    spacing=20,
                    expand=True
                ),
                analyze,
                ft.Row([ft.ElevatedButton(text='生成查询值',
                                          on_click=lambda _: self.business_logic(
                                              file_path_text,
                                              sheet_selector,
                                              columns_selector,
                                              handel_progress,
                                              markdown,
                                              markdown_area
                                          )
                                          )
                        ],
                       alignment=ft.MainAxisAlignment.CENTER,
                       expand=True
                       ),
                handel_progress,
                markdown_area

            ],  # 整个页面内容垂直居中
            spacing=30,
        )

    def business_logic(self,
                       file_path_text: ft.TextField,
                       sheet_selector: ft.Dropdown,
                       columns_selector: ft.Dropdown,
                       progress: ProgressRingComponent,
                       markdown: ft.Markdown,
                       markdown_area: ft.Container
                       ):
        try:
            markdown_area.visible=False
            markdown.value = ''
            self.page.update()
            if file_path_text.value in [None, '']:
                raise RuntimeError('未提供源文件')
            progress.update_status(ProgressStatus.LOADING, '开始待查询语句所需的值')
            file_name = Path(file_path_text.value).stem
            # 根据列拆分
            progress.update_status(ProgressStatus.LOADING, '开始读取源文件')
            df = pd.read_excel(file_path_text.value, sheet_name=sheet_selector.value)
            progress.update_status(ProgressStatus.LOADING, '开始生成')
            tmp_set  = set(df[columns_selector.value].tolist())
            out_put = ','.join(
                f"'00{str(value)}'" if str(value).isdigit() and len(str(value)) == 10 else f"'{str(value)}'"
                for value in tmp_set
            )
            progress.update_status(ProgressStatus.LOADING, '生成结果')
            markdown.value = out_put
            if markdown.value:
                markdown_area.visible = True
                progress.update_status(ProgressStatus.SUCCESS, '生成成功,结果展示存在延迟')
            else:
                raise RuntimeError("无任何数据生成")
            self.page.update()

        except Exception as e:
            progress.update_status(ProgressStatus.ERROR, str(e))

