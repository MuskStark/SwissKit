from enum import Enum

import flet as ft


class ProgressRingComponent(ft.Column):
    def __init__(self):
        super().__init__()
        self.progress = ft.ProgressRing(visible=False)
        self.finished_icon = ft.Icon(ft.Icons.DONE, color="green", visible=False)
        self.error_icon = ft.Icon(ft.Icons.ERROR, color="red", visible=False)
        self.progress_text = ft.Text(value="")
        self.controls.extend([ft.Row([self.progress, self.finished_icon, self.error_icon], alignment=ft.MainAxisAlignment.CENTER), ft.Row([self.progress_text],alignment=ft.MainAxisAlignment.CENTER)])

    def update_status(self, status_enum: Enum, text: str = ""):
        """更新进度状态
        :param status_enum: 状态枚举
        :param text: 显示的文本
        """
        if status_enum.value == "loading":
            self.progress.visible = True
            self.finished_icon.visible = False
            self.error_icon.visible = False
        elif status_enum.value == "success":
            self.progress.visible = False
            self.finished_icon.visible = True
            self.error_icon.visible = False
        elif status_enum.value == "error":
            self.progress.visible = False
            self.finished_icon.visible = False
            self.error_icon.visible = True

        self.progress_text.value = text
        self.update()  # 触发 UI 更新