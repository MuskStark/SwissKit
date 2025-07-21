import flet as ft
from typing import List

class SearchComponent(ft.Column):
    def __init__(self, placeholder: str = "Search..."):
        super().__init__()
        self.data = []
        self.placeholder = placeholder

        self.search = ft.SearchBar(
            view_elevation=4,
            divider_color=ft.Colors.AMBER,
            bar_hint_text=self.placeholder,
            view_hint_text="Choose from the suggestions...",
            on_change=self.handle_change,
            on_submit=self.handle_submit,
            on_tap= lambda e:self.handle_tap(e),
            controls=[]  # 初始化为空
        )

        # 添加到 Column 控件
        self.controls.append(self.search)

    def close_anchor(self, e):
        """点击 ListTile 关闭搜索视图"""
        text = f"Selected: {e.control.data}"
        print(text)
        self.search.close_view(text)

    def handle_change(self, e):
        print(f"handle_change e.data: {e.data}")

    def handle_submit(self, e):
        print(f"handle_submit e.data: {e.data}")

    def handle_tap(self, e):
        print("handle_tap")
        self.search.open_view()

    def load_data(self, data_list: List[str]):
        """加载搜索数据"""
        self.data = data_list
        self.search.controls = [
            ft.ListTile(title=ft.Text(f"{value}"), on_click=self.close_anchor, data=value)
            for value in self.data
        ]
        self.search.update()

    def get_data(self):
        """获取当前搜索数据"""
        return self.search.data

    def set_placeholder(self, text: str):
        """动态修改搜索框提示文本"""
        self.search.bar_hint_text = text
        self.search.update()