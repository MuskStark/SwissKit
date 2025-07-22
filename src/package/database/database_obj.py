import os
import platform
import sys
from functools import lru_cache
from pathlib import Path

from peewee import SqliteDatabase

from ..util.path_util import PathUtil


@lru_cache(maxsize=None)
class DataBaseObj:
    def __init__(self):
        """获取数据存储目录（推荐用于数据库等持久化数据）"""
        system = platform.system()

        if PathUtil.is_flet_packaged():
            # 打包后的环境
            if system == "Darwin":  # macOS
                # 使用用户应用程序支持目录（推荐）
                home = Path.home()
                app_name = Path(sys.executable).stem  # 获取应用名称
                data_dir = home / "Library" / "Application Support" / app_name
            elif system == "Windows":
                # Windows AppData
                app_name = Path(sys.executable).stem
                data_dir = Path(os.environ.get('APPDATA', '')) / app_name
            else:  # Linux
                # XDG 标准
                app_name = Path(sys.executable).stem.lower()
                data_dir = Path.home() / ".local" / "share" / app_name
        else:
            # 开发环境 - 使用项目根目录下的 data 文件夹
            data_dir = PathUtil.get_app_root() / "database-test"

        # 确保目录存在
        data_dir.mkdir(parents=True, exist_ok=True)
        self.db = SqliteDatabase(str(data_dir / 'swisskitdb.db'))