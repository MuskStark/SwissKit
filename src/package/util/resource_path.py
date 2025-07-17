import sys
import os
from typing_extensions import LiteralString


def resource_path(relative_path) -> LiteralString | str | bytes:
    """ 获取资源文件的绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        # 打包后资源被解压到临时目录 _MEIPASS
        base_path = sys._MEIPASS
    else:
        # 开发环境使用当前文件所在目录
        base_path = os.path.abspath("")
    return os.path.join(base_path, relative_path)