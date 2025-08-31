import os
import platform
import sys
from functools import lru_cache
from pathlib import Path

from peewee import SqliteDatabase

from ..util.log_util import get_logger
from ..util.path_util import PathUtil


@lru_cache(maxsize=None)
class DataBaseObj:
    def __init__(self):
        self.logger = get_logger('DataBase')
        self.logger.info('开始判断程序所属环境')
        system = platform.system()

        if PathUtil.is_flet_packaged():
            self.logger.info('所属环境为生产环境')
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
            self.logger.info('所属环境为开发环境')
            # 开发环境 - 使用项目根目录下的 data 文件夹
            data_dir = PathUtil.get_app_root() / "database-test"
        self.logger.info('开始初始化数据库')
        # 确保目录存在
        data_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f'创建数据库文件夹：{data_dir}')
        self.db = SqliteDatabase(str(data_dir / 'swisskitdb.db'))
        self.logger.info(f'创建数据库本体：{str(data_dir / "swisskitdb.db")}')

    def creat_table(self, models: list, need_check: bool = True, safe: bool = True):
        self.logger.info("开始创建数据表")
        connection_was_closed = self.db.is_closed()
        try:
            if connection_was_closed:
                self.logger.info("数据库连接已关闭，正在连接...")
                self.db.connect()
            else:
                self.logger.info("数据库连接已存在，跳过连接步骤")
            if need_check:
                for model in models:
                    self.logger.info(f'开始检查{model}是否存在')
                    if not model.table_exists():
                        self.logger.info(f'开始创建{model}')
                        model.create_table(safe=safe)
            else:
                self.logger.info(f'开始创建{models}')
                self.db.create_tables(models, safe=safe)
        except Exception as e:
            self.logger.error(f'创建失败{e}')
        finally:
            if not self.db.is_closed():
                self.db.close()

    def drop_table(self, models: list, safe: bool = True):
        self.logger.info(f'开始移除指定数据表{models}')
        try:
            self.db.connect()
            for model in models:
                if model.table_exists():
                    self.logger.info(f'开始移除{model}')
                    model.drop_table(safe=safe)
        except Exception as e:
            self.logger.error(f'移除数据表过程中出错:{e}')
        finally:
            if not self.db.is_closed():
                self.db.close()
