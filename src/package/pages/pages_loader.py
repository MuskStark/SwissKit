import asyncio

import flet as ft

from .page_facroty import PageFactory


async def loader(index: int, page: ft.Page):
        return PageFactory.create_page(index, page).gui()


def update_content(index: int, content: ft.Column, page: ft.Page):
    # 运行 async loader()，并等待它完成
    gui = asyncio.run(loader(index, page))
    content.controls.clear()
    content.controls.append(gui)
    page.update()
