import os
import platform

import picologging as logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json

from .path_util import PathUtil


class LoggerUtility:

    def __init__(
            self,
            name: str = "SwissKit",
            log_level: str = "INFO",
            console_output: bool = False,
            file_output: bool = True,
            json_format: bool = False,
            max_bytes: int = 10 * 1024 * 1024,  # 10MB
            backup_count: int = 5
    ):
        """
        初始化日志工具类

        Args:
            name: 日志器名称
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            json_format: 是否使用JSON格式输出
            max_bytes: 日志文件最大字节数
            backup_count: 日志文件备份数量
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.console_output = console_output
        self.file_output = file_output
        self.json_format = json_format
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # 设置日志目录
        system = platform.system()
        if PathUtil.is_flet_packaged():
            # 打包后的环境
            if system == "Darwin":  # macOS
                home = Path.home()
                app_name = Path(sys.executable).stem
                log_dir = home / "Library" / "Application Support" / app_name / 'log'
            elif system == "Windows":
                # Windows AppData
                app_name = Path(sys.executable).stem
                log_dir = Path(os.environ.get('APPDATA', '')) / app_name / 'log'
            else:  # Linux
                # XDG 标准
                app_name = Path(sys.executable).stem.lower()
                log_dir = Path.home() / ".local" / "share" / app_name / 'log'
        else:
            # 开发环境
            self.console_output = True
            log_dir = PathUtil.get_app_root() / "log"

        # 确保目录存在
        log_dir.mkdir(parents=True, exist_ok=True)

        self.log_dir = Path(log_dir)

        if self.file_output:
            self.log_dir.mkdir(exist_ok=True)

        # 创建logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)

        # 清除已存在的处理器
        self.logger.handlers.clear()

        # 设置格式化器
        self._setup_formatters()

        # 添加处理器
        if self.console_output:
            self._add_console_handler()

        if self.file_output:
            self._add_file_handler()

    def _setup_formatters(self):
        """设置日志格式化器"""
        if self.json_format:
            # JSON格式化器
            self.formatter = JsonFormatter()
        else:
            # 标准格式化器
            format_string = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "[%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"
            )
            self.formatter = logging.Formatter(
                format_string,
                datefmt="%Y-%m-%d %H:%M:%S"
            )

    def _add_console_handler(self):
        """添加控制台处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self):
        """添加文件处理器"""
        from picologging.handlers import RotatingFileHandler

        # 为每个logger创建独立的子目录
        logger_dir = self.log_dir / self.name
        logger_dir.mkdir(exist_ok=True, parents=True)

        # 生成日志文件路径
        log_filename = f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = logger_dir / log_filename

        # 创建旋转文件处理器
        file_handler = RotatingFileHandler(
            str(log_path),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """获取logger实例"""
        return self.logger

    def debug(self, message: str, **kwargs):
        """记录DEBUG级别日志"""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """记录INFO级别日志"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """记录WARNING级别日志"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """记录ERROR级别日志"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """记录CRITICAL级别日志"""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)

    def exception(self, message: str, **kwargs):
        """记录异常信息"""
        self.logger.exception(message, extra=kwargs)

    def set_level(self, level: str):
        """动态设置日志级别"""
        new_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(new_level)
        for handler in self.logger.handlers:
            handler.setLevel(new_level)

    def add_context(self, **context):
        """添加上下文信息到日志"""
        for handler in self.logger.handlers:
            handler.addFilter(ContextFilter(context))


class JsonFormatter(logging.Formatter):
    """JSON格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process,
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, 'extra'):
            for key, value in record.__dict__.items():
                if key not in log_data and not key.startswith('_'):
                    log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False)


class ContextFilter(logging.Filter):
    """上下文过滤器，用于添加额外的上下文信息"""

    def __init__(self, context: Dict[str, Any]):
        super().__init__()
        self.context = context

    def filter(self, record: logging.LogRecord) -> bool:
        """添加上下文信息到日志记录"""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


# 创建全局logger缓存
_logger_cache = {}


def get_logger(
        name: str = "SwissKit",
        log_level: str = "INFO",
        **kwargs
) -> LoggerUtility:
    """
    获取或创建logger实例

    Args:
        name: 日志器名称
        log_level: 日志级别
        **kwargs: 其他LoggerUtility初始化参数

    Returns:
        LoggerUtility实例
    """
    global _logger_cache

    # 如果logger已存在，直接返回
    if name in _logger_cache:
        return _logger_cache[name]

    # 创建新的logger并缓存
    logger = LoggerUtility(name=name, log_level=log_level, **kwargs)
    _logger_cache[name] = logger

    return logger