import flet as ft

from ..enums.layout_enums import Layout


class MultiSelectComponent(ft.Container):
    """
    多选组件 - 继承自 ft.Row 实现复合控件
    支持单个选项选择/取消、全选、清除所有选项
    """

    def __init__(self, dropdown_label: str = None, options: list[str] = None, title="多选组件", tag_list: list[str]=None, on_change=None, layout=Layout.Horizontal):
        super().__init__()
        self.dropdown_label = dropdown_label or "选择选项"
        self.options_list = options or []
        self.control_name = title
        self.on_change = on_change
        self.tag_list = tag_list or []
        self.layout = layout
        self.need_update_page = False

        # 创建组件
        self.dropdown = ft.Dropdown(
            label=self.dropdown_label,
            options=[ft.DropdownOption(value) for value in self.options_list],
            on_change=self._tag_dropdown_changed,
            width=300
        )

        self.tag_display = ft.Row(wrap=True)

        if self.layout == Layout.Horizontal:
            self.content = ft.Row(controls=[self.dropdown, self.tag_display], expand=True)
        elif self.layout == Layout.Vertical:
            self.content = ft.Column(controls=[self.dropdown, self.tag_display], expand=True)
        if self.tag_list:
            self.need_update_page =True

        self.expand = True

    def did_mount(self):
        """控件挂载后的回调"""
        if self.need_update_page:
            self._update_tag_display()

    def will_unmount(self):
        """控件卸载前的回调"""
        pass


    def is_isolated(self):
        return True

    def _tag_dropdown_changed(self, e):
        if e.control.value and e.control.value not in self.tag_list:
            self.tag_list.append(e.control.value)
            self._update_tag_display()
            # 触发外部回调
            if self.on_change:
                self.on_change(self.tag_list.copy())
        e.control.value = None  # 重置选择
        e.control.update()

    def _update_tag_display(self):
        self.tag_display.controls.clear()
        for item in self.tag_list:
            chip = ft.Container(
                content=ft.Row([
                    ft.Text(item, size=14),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=16,
                        on_click=lambda e, item=item: self._remove_item(item),
                        tooltip="删除"
                    )
                ], tight=True),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                bgcolor=ft.Colors.BLUE_100,
                border_radius=16,
                margin=ft.margin.only(right=4, bottom=4)
            )
            self.tag_display.controls.append(chip)
        try:
            self.update()
        except AttributeError:
            pass

    def _remove_item(self, item):
        if item in self.tag_list:
            self.tag_list.remove(item)
            self._update_tag_display()
            # 触发外部回调
            if self.on_change:
                self.on_change(self.tag_list.copy())

    def get_selected_values(self):
        """获取当前选中的所有值"""
        return self.tag_list.copy()

    def clear_all(self):
        """清空所有选中项"""
        self.tag_list.clear()
        self._update_tag_display()

    def set_values(self, values: list[str]):
        """设置选中的值"""
        self.tag_list = [v for v in values if v in self.options_list]
        self._update_tag_display()

    def add_option(self, option: str):
        """动态添加选项"""
        if option not in self.options_list:
            self.options_list.append(option)
            self.dropdown.options.append(ft.DropdownOption(option))
            self.dropdown.update()

    def remove_option(self, option: str):
        """动态移除选项"""
        if option in self.options_list:
            self.options_list.remove(option)
            self.dropdown.options = [opt for opt in self.dropdown.options if opt.key != option]
            if option in self.tag_list:
                self.tag_list.remove(option)
                self._update_tag_display()
            else:
                self.dropdown.update()

    def select_all(self):
        """选择所有选项"""
        self.tag_list = self.options_list.copy()
        self._update_tag_display()
        if self.on_change:
            self.on_change(self.tag_list.copy())