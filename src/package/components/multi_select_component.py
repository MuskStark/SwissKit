import flet as ft


class MultiSelectComponent(ft.Control):
    """
    多选组件
    支持单个选项选择/取消、全选、清除所有选项
    """

    def __init__(self, options=None, title="多选组件", on_change=None):
        super().__init__()
        self.options = options or []
        self.title = title
        self.selected_items = set()
        self.on_change_callback = on_change

        # 控件引用
        self.checkbox_controls = {}
        self.select_all_checkbox = None
        self.selected_count_text = None
        self.selected_items_container = None

    def _get_control_name(self) -> str:
        return f"{self.title}"

    def build(self):
        # 创建选择框
        self.checkbox_controls = {}
        checkboxes = []

        for option in self.options:
            checkbox = ft.Checkbox(
                label=option,
                value=False,
                on_change=self.on_item_change
            )
            self.checkbox_controls[option] = checkbox
            checkboxes.append(checkbox)

        # 全选复选框
        self.select_all_checkbox = ft.Checkbox(
            label="全选",
            value=False,
            on_change=self.on_select_all
        )

        # 已选择数量显示
        self.selected_count_text = ft.Text(
            value="已选择: 0 项",
            size=12,
            color=ft.Colors.GREY_700
        )

        # 已选择项目显示区域
        self.selected_items_container = ft.Column(
            controls=[],
            spacing=5
        )

        # 清除按钮
        clear_button = ft.ElevatedButton(
            text="清除所有",
            icon=ft.Icons.CLEAR,
            on_click=self.clear_all,
            style=ft.ButtonStyle(
                color=ft.Colors.RED_400,
                bgcolor=ft.Colors.RED_50
            )
        )

        # 获取已选择项按钮
        get_selected_button = ft.ElevatedButton(
            text="获取选中项",
            icon=ft.Icons.LIST,
            on_click=self.show_selected,
            style=ft.ButtonStyle(
                color=ft.Colors.BLUE_400,
                bgcolor=ft.Colors.BLUE_50
            )
        )

        return ft.Container(
            content=ft.Column([
                # 标题
                ft.Text(
                    value=self.title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700
                ),
                ft.Divider(height=1),

                # 控制按钮区域
                ft.Row([
                    self.select_all_checkbox,
                    self.selected_count_text,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # 主要内容区域 - 左右布局
                ft.Row([
                    # 左侧：可选项区域
                    ft.Container(
                        content=ft.Column([
                            ft.Text("可选项目", size=14, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Column(
                                    controls=checkboxes,
                                    spacing=5,
                                    scroll=ft.ScrollMode.AUTO
                                ),
                                height=180,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                border_radius=5,
                                padding=10,
                                bgcolor=ft.Colors.GREY_50
                            ),
                        ], spacing=5),
                        width=160
                    ),

                    # 右侧：已选择项区域
                    ft.Container(
                        content=ft.Column([
                            ft.Text("已选择项目", size=14, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Column([
                                    self.selected_items_container
                                ], scroll=ft.ScrollMode.AUTO),
                                height=180,
                                border=ft.border.all(1, ft.Colors.BLUE_300),
                                border_radius=5,
                                padding=10,
                                bgcolor=ft.Colors.BLUE_50
                            ),
                        ], spacing=5),
                        width=160
                    ),
                ], spacing=10),

                # 操作按钮
                ft.Row([
                    clear_button,
                    get_selected_button,
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            ], spacing=10),

            padding=15,
            border=ft.border.all(1, ft.Colors.BLUE_200),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            width=370  # 增加宽度以容纳两列布局
        )

    def on_item_change(self, e):
        """单个选项改变时的处理"""
        checkbox = e.control
        option = checkbox.label

        if checkbox.value:
            self.selected_items.add(option)
        else:
            self.selected_items.discard(option)

        self.update_ui()

        # 调用回调函数
        if self.on_change_callback:
            self.on_change_callback(list(self.selected_items))

    def on_select_all(self, e):
        """全选/取消全选"""
        select_all = e.control.value

        for option, checkbox in self.checkbox_controls.items():
            checkbox.value = select_all

        if select_all:
            self.selected_items = set(self.options)
        else:
            self.selected_items.clear()

        self.update_ui()

        # 调用回调函数
        if self.on_change_callback:
            self.on_change_callback(list(self.selected_items))

    def clear_all(self, e):
        """清除所有选择"""
        self.selected_items.clear()

        # 更新所有复选框状态
        for checkbox in self.checkbox_controls.values():
            checkbox.value = False

        self.select_all_checkbox.value = False
        self.update_ui()

        # 调用回调函数
        if self.on_change_callback:
            self.on_change_callback([])

    def update_ui(self):
        """更新UI状态"""
        # 更新选择数量显示
        count = len(self.selected_items)
        self.selected_count_text.value = f"已选择: {count} 项"

        # 更新全选按钮状态
        if count == 0:
            self.select_all_checkbox.value = False
        elif count == len(self.options):
            self.select_all_checkbox.value = True
        else:
            self.select_all_checkbox.value = None  # 部分选中状态

        # 更新已选择项目显示
        self.update_selected_items_display()

        self.update()

    def update_selected_items_display(self):
        """更新已选择项目的显示区域"""
        self.selected_items_container.controls.clear()

        if not self.selected_items:
            self.selected_items_container.controls.append(
                ft.Text(
                    "未选择任何项目",
                    size=12,
                    color=ft.Colors.GREY_500,
                    italic=True
                )
            )
        else:
            for item in sorted(self.selected_items):
                # 创建每个已选择项目的显示行
                item_row = ft.Container(
                    content=ft.Row([
                        ft.Text(
                            item,
                            size=12,
                            expand=True,
                            color=ft.Colors.BLUE_800
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            tooltip=f"移除 {item}",
                            on_click=lambda e, item_name=item: self.remove_single_item(item_name),
                            style=ft.ButtonStyle(
                                color=ft.Colors.RED_400,
                                padding=ft.padding.all(4)
                            )
                        )
                    ], spacing=5, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=15,
                    bgcolor=ft.Colors.BLUE_100,
                    border=ft.border.all(1, ft.Colors.BLUE_200)
                )
                self.selected_items_container.controls.append(item_row)

    def remove_single_item(self, item):
        """移除单个已选择的项目"""
        if item in self.selected_items:
            self.selected_items.discard(item)

            # 更新对应的复选框状态
            if item in self.checkbox_controls:
                self.checkbox_controls[item].value = False

            self.update_ui()

            # 调用回调函数
            if self.on_change_callback:
                self.on_change_callback(list(self.selected_items))

    def show_selected(self, e):
        """显示已选择的项"""
        if self.selected_items:
            selected_list = "\n".join([f"• {item}" for item in sorted(self.selected_items)])
            message = f"已选择的项目:\n\n{selected_list}"
        else:
            message = "未选择任何项目"

        # 显示对话框
        dialog = ft.AlertDialog(
            title=ft.Text("选择结果"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("确定", on_click=lambda _: self.close_dialog(dialog))
            ]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self, dialog):
        """关闭对话框"""
        dialog.open = False
        self.page.update()

    def get_selected_items(self):
        """获取已选择的项目列表"""
        return list(self.selected_items)

    def set_selected_items(self, items):
        """设置选中的项目"""
        self.selected_items = set(items)

        # 更新复选框状态
        for option, checkbox in self.checkbox_controls.items():
            checkbox.value = option in self.selected_items

        self.update_ui()
