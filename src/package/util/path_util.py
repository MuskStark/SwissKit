import os
import platform
import sys
from pathlib import Path


class PathUtil:
    @staticmethod
    def is_flet_packaged():
        """准确判断是否为 Flet 打包后的应用"""

        # 方法1: 检查 Flet 特定的环境变量
        if os.environ.get('FLET_APP_HIDDEN'):
            return True

        # 方法2: 检查是否在 Flet 的临时解压目录中运行
        # Flet 0.28+ 版本的特征
        current_dir = Path(sys.executable).parent
        current_path_str = str(current_dir).lower()

        # macOS: Flet 打包后通常在 /private/var/folders/... 或 Application Support 下
        if platform.system() == "Darwin":
            if any(marker in current_path_str for marker in [
                '/private/var/folders/',
                '/library/caches/',
                'appdata/local/temp',
                '/contents/macos'
            ]):
                return True

        # Windows: 检查临时目录特征
        elif platform.system() == "Windows":
            if any(marker in current_path_str for marker in [
                '\\appdata\\local\\temp\\',
                '\\temp\\flet',
                '\\_internal\\'
            ]):
                return True

        # Linux: 检查临时目录
        else:
            if any(marker in current_path_str for marker in [
                '/tmp/',
                '/.local/share/',
                '/_internal/'
            ]):
                return True

        # 方法3: 检查 Flet 打包后的文件结构
        # 查找 Flet 特有的文件
        flet_markers = [
            current_dir / "flet.dll",  # Windows
            current_dir / "libflet.so",  # Linux
            current_dir / "libflet.dylib",  # macOS
            current_dir.parent / "_internal",  # 通用
            current_dir / "base_library.zip"  # PyInstaller
        ]

        if any(marker.exists() for marker in flet_markers):
            return True

        # 方法4: 检查进程名称
        # Flet 打包后的应用名称通常不是 python
        exec_name = Path(sys.executable).name.lower()
        if exec_name not in ['python', 'python3', 'python.exe', 'python3.exe']:
            # 额外检查：确保不是在 IDE 中运行
            if 'pycharm' not in exec_name and 'code' not in exec_name:
                return True

        return False
    @staticmethod
    def get_app_root():
        """获取应用程序根目录（跨平台）"""
        if PathUtil.is_flet_packaged():
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
