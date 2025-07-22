import tomllib

import flet as ft

from package.components import navigation
from package.database.database_obj import DataBaseObj
from package.pages import pages_loader
from package.util.resource_path import resource_path


async def main(page: ft.Page):
    # 加载配置文件
    with open(resource_path('assets/config.toml'), 'br') as config:
        config = tomllib.load(config)
    # 初始加载提示
    page.title = "Swiss Kit-" + config['version']
    init_progress = ft.ProgressRing(width=20, height=20, stroke_width=2)
    loading_text = ft.Text("工具初始化中...", style=ft.TextThemeStyle.BODY_MEDIUM)
    loading_row = ft.Row(
        [init_progress, loading_text],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    page.add(loading_row)
    page.update()

    # 初始化主界面

    # 页面基础设置
    page.title = "Swiss Kit-" + config['version']
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # 创建内容容器
    content = ft.Column(
        [await pages_loader.loader(0, page)],
        alignment=ft.MainAxisAlignment.START,
        expand=True
    )

    # 清除加载提示
    page.clean()

    DataBaseObj().db.connect()

    # 添加主界面
    page.add(
        ft.Row(
            [
                navigation.navigation_gui(content, page, special_modl=config['special_modl']),
                ft.VerticalDivider(width=1),
                content
            ],
            expand=True
        )
    )
    page.update()


ft.app(main)
