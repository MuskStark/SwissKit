import flet as ft

class FileOrPathPicker(ft.Column):

    def __init__(self, page: ft.Page, button_icon:ft.Icons, is_pick_file:bool, text_label:str):
        super().__init__()
        self.page = page
        self.is_pick_file = is_pick_file
        self.picker  = ft.FilePicker(on_result= lambda e: self._picker_result(e))
        self.text = ft.TextField(label=text_label, read_only=True, expand=True)
        self.page.overlay.append(self.picker)
        self.button = ft.IconButton(
                        icon=button_icon,
                        style=ft.ButtonStyle(shape=ft.CircleBorder()),  # 让按钮变成圆形
                        on_click=lambda _: self._button_on_click()
                    )
        self.controls.append(ft.Row([self.button, self.text], expand=True))

    def _picker_result(self, e):
        if self.is_pick_file:
            if e.files:
                self.text.value = e.files[0].path
        else:
            if e.path:
                self.text.value = e.path
        self.page.update()
    def _button_on_click(self):
        if self.is_pick_file:
            self.picker.pick_files()
        else:
            self.picker.get_directory_path()

    def get_pick_value(self):
        return self.text.value


