import sys
from pathlib import Path


class PathUtil:
    @staticmethod
    def get_app_root():
        """获取应用程序根目录（跨平台）"""
        if getattr(sys, 'frozen', False):
            # 打包后的程序
            if hasattr(sys, '_MEIPASS'):
                return Path(sys.executable).parent
            else:
                return Path(sys.executable).parent
        else:
            # 开发环境
            current_file = Path(__file__).resolve()
            # 向上遍历目录，直到找到包含 `main.py` 的目录
            while current_file.parent != current_file:
                if (current_file / 'main.py').exists():
                    return current_file
                current_file = current_file.parent
            raise FileNotFoundError("Could not find the application root directory.")
