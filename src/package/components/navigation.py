import flet as ft

from ..pages import pages_loader

DEFAULT_THEME = {
    "text_color": ft.Colors.GREY_600,
    "selected_text_color": ft.Colors.GREEN_300,
    "footer_size": 12,
    "rail_width": 100,
    "divider_color": ft.Colors.GREY_300
}


def navigation_gui(
        content,
        page: ft.Page,
        special_modl: bool = False,
        destinations: list[ft.NavigationRailDestination] = None,
        copyright_text: str = "CopyRight © 2025 Summer",
        theme: dict = None
):
    # 合并主题配置
    theme = {**DEFAULT_THEME, **(theme or {})}

    # 事件处理函数
    def handle_nav_change(e):
        if 0 <= e.control.selected_index < len(e.control.destinations):
            pages_loader.update_content(e.control.selected_index, content, page)
            page.update()
        else:
            print(f"Invalid navigation index: {e.control.selected_index}")

    # 导航栏配置
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=theme["rail_width"],
        leading=ft.FloatingActionButton(
            icon=ft.Icons.COPYRIGHT,
            tooltip=copyright_text,  # 使用 tooltip 替代文本
            mini=True
        ),
        group_alignment=-0.9,
        destinations=destinations or [
            ft.NavigationRailDestination(
                icon=ft.Icons.LOCAL_GAS_STATION_OUTLINED,
                selected_icon=ft.Icons.LOCAL_GAS_STATION,
                label="Excel增加英文列工具"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SPLITSCREEN_OUTLINED,
                selected_icon=ft.Icons.SPLITSCREEN,
                label="Excel文件拆分工具"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.QUERY_STATS_OUTLINED,
                selected_icon=ft.Icons.QUERY_STATS,
                label="Sql待查询值生成",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.QUERY_STATS_OUTLINED,
                selected_icon=ft.Icons.QUERY_STATS,
                label="邮件批量发送",
            )
        ],
        on_change=handle_nav_change,
        expand=True,
        # indicator_shape=ft.ContinuousRectangleBorder(radius=0), #选中阴影样式
        selected_label_text_style=ft.TextStyle(
            weight=ft.FontWeight.BOLD,
            color=theme["selected_text_color"]
        ),
        unselected_label_text_style=ft.TextStyle(
            color=theme["text_color"]
        ),
    )

    return ft.Container(
        width=theme["rail_width"],
        content=ft.Column(
            controls=[
                rail,
                ft.Divider(
                    height=1,
                    color=theme["divider_color"]
                ),
                ft.Container(
                    padding=10,
                    content=ft.Text(
                        copyright_text,
                        size=theme["footer_size"],
                        color=theme["text_color"],
                        text_align=ft.TextAlign.CENTER
                    )
                )
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True
        ),
        # shadow=ft.BoxShadow(
        #     spread_radius=1,
        #     blur_radius=8,
        #     color=ft.Colors.BLACK12,
        #     offset=ft.Offset(2, 0)
        # )
    )