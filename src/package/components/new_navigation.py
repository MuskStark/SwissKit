import importlib
import inspect
import os
from pathlib import Path
from typing import List, Dict, Type, Any
from abc import ABC, abstractmethod


class ToolBoxPage(ABC):
    def __init__(self, page):
        self.page = page

    @abstractmethod
    def gui(self):
        pass


# 方法1: 配置文件驱动的动态导入
class PageConfig:
    """页面配置管理"""

    # 页面配置映射
    PAGE_MODULES = {
        "excel_split_v2": {
            "module": "page.excel_split_v2",
            "class": "ExcelSplitPageV2",
            "label": "Excel文件拆分工具",
            "icon": "SPLITSCREEN_OUTLINED",
            "selected_icon": "SPLITSCREEN",
            "order": 2
        },
        "odap_formater": {
            "module": "page.odap_formater",
            "class": "ODAPFormater",
            "label": "智数平台工具",
            "icon": "LOCAL_GAS_STATION_OUTLINED",
            "selected_icon": "LOCAL_GAS_STATION",
            "order": 1
        },
        "guan_hu_match": {
            "module": "page.guan_hu_match",
            "class": "Relationship",
            "label": "管户数据处理",
            "icon": "ACCOUNT_BOX_OUTLINED",
            "selected_icon": "ACCOUNT_BOX",
            "order": 0
        },
        "odap_search_value": {
            "module": "page.odap_search_value",
            "class": "ODAPSearchValue",
            "label": "智数待查询值生成",
            "icon": "QUERY_STATS_OUTLINED",
            "selected_icon": "QUERY_STATS",
            "order": 3
        },
        "innovation": {
            "module": "page.innovation",
            "class": "Innovation",
            "label": "创新委评分汇总工具",
            "icon": "DESKTOP_WINDOWS_OUTLINED",
            "selected_icon": "DESKTOP_WINDOWS",
            "order": 4,
            "visible_condition": lambda ctx: ctx.get('special_modl', False)
        }
    }


class DynamicPageImporter:
    """动态页面导入器"""

    def __init__(self, base_package: str = ""):
        self.base_package = base_package
        self._imported_classes: Dict[str, Type] = {}
        self._failed_imports: List[str] = []

    def import_page_class(self, module_name: str, class_name: str) -> Type[ToolBoxPage]:
        """动态导入单个页面类"""
        cache_key = f"{module_name}.{class_name}"

        if cache_key in self._imported_classes:
            return self._imported_classes[cache_key]

        try:
            # 构建完整的模块名
            if self.base_package:
                full_module_name = f"{self.base_package}.{module_name}"
            else:
                full_module_name = module_name

            # 动态导入模块
            module = importlib.import_module(full_module_name)

            # 获取类
            page_class = getattr(module, class_name)

            # 验证是否继承自ToolBoxPage
            if not issubclass(page_class, ToolBoxPage):
                raise TypeError(f"{class_name} must inherit from ToolBoxPage")

            # 缓存类
            self._imported_classes[cache_key] = page_class

            print(f"✓ Successfully imported {class_name} from {full_module_name}")
            return page_class

        except ImportError as e:
            error_msg = f"Failed to import {class_name} from {module_name}: {e}"
            self._failed_imports.append(error_msg)
            print(f"✗ {error_msg}")
            return None
        except AttributeError as e:
            error_msg = f"Class {class_name} not found in {module_name}: {e}"
            self._failed_imports.append(error_msg)
            print(f"✗ {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Unexpected error importing {class_name}: {e}"
            self._failed_imports.append(error_msg)
            print(f"✗ {error_msg}")
            return None

    def import_all_pages(self, page_configs: Dict[str, Dict]) -> Dict[str, Type[ToolBoxPage]]:
        """批量导入所有页面"""
        imported_pages = {}

        for page_key, config in page_configs.items():
            page_class = self.import_page_class(config["module"], config["class"])
            if page_class:
                imported_pages[page_key] = page_class

        return imported_pages

    def get_failed_imports(self) -> List[str]:
        """获取导入失败的信息"""
        return self._failed_imports.copy()


# 方法2: 目录扫描式动态导入
class DirectoryPageScanner:
    """目录扫描式页面发现器"""

    def __init__(self, page_directory: str):
        self.page_directory = Path(page_directory)
        self._discovered_pages: Dict[str, Type[ToolBoxPage]] = {}

    def scan_directory(self) -> Dict[str, Type[ToolBoxPage]]:
        """扫描目录中的所有页面"""
        if not self.page_directory.exists():
            print(f"Directory {self.page_directory} does not exist")
            return {}

        discovered_pages = {}

        for py_file in self.page_directory.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                # 构建模块名
                module_name = f"page.{py_file.stem}"

                # 动态导入模块
                module = importlib.import_module(module_name)

                # 查找所有继承自ToolBoxPage的类
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                            issubclass(obj, ToolBoxPage) and
                            obj != ToolBoxPage):
                        discovered_pages[py_file.stem] = obj
                        print(f"✓ Discovered page class {name} in {module_name}")

            except Exception as e:
                print(f"✗ Failed to scan {py_file}: {e}")

        return discovered_pages


# 方法3: 装饰器+自动发现
class AutoDiscoveryRegistry:
    """自动发现注册表"""

    _registered_pages: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_page(cls, key: str, module_path: str, class_name: str, **kwargs):
        """注册页面信息"""
        cls._registered_pages[key] = {
            "module": module_path,
            "class": class_name,
            **kwargs
        }

    @classmethod
    def get_all_pages(cls) -> Dict[str, Dict[str, Any]]:
        """获取所有注册的页面"""
        return cls._registered_pages.copy()

    @classmethod
    def import_registered_pages(cls, importer: DynamicPageImporter) -> Dict[str, Type[ToolBoxPage]]:
        """导入所有注册的页面"""
        return importer.import_all_pages(cls._registered_pages)


# 自动注册装饰器
def auto_register_page(key: str, label: str, icon: str, selected_icon: str,
                       order: int = 0, **kwargs):
    """自动注册页面装饰器"""

    def decorator(cls: Type[ToolBoxPage]):
        # 获取模块信息
        module_path = cls.__module__
        class_name = cls.__name__

        # 注册到全局注册表
        AutoDiscoveryRegistry.register_page(
            key=key,
            module_path=module_path,
            class_name=class_name,
            label=label,
            icon=icon,
            selected_icon=selected_icon,
            order=order,
            **kwargs
        )

        return cls

    return decorator


# 改进的PageFactory
class EnhancedPageFactory:
    """增强的页面工厂"""

    def __init__(self, base_package: str = ""):
        self.importer = DynamicPageImporter(base_package)
        self.scanner = DirectoryPageScanner("page")
        self._page_classes: Dict[str, Type[ToolBoxPage]] = {}
        self._page_instances: Dict[str, ToolBoxPage] = {}
        self._initialized = False

    def initialize(self, import_method: str = "config"):
        """初始化页面工厂"""
        if self._initialized:
            return

        if import_method == "config":
            # 使用配置文件方式
            self._page_classes = self.importer.import_all_pages(PageConfig.PAGE_MODULES)
        elif import_method == "scan":
            # 使用目录扫描方式
            self._page_classes = self.scanner.scan_directory()
        elif import_method == "auto":
            # 使用自动发现方式
            self._page_classes = AutoDiscoveryRegistry.import_registered_pages(self.importer)
        else:
            raise ValueError(f"Unknown import method: {import_method}")

        self._initialized = True

        # 报告导入结果
        print(f"Successfully imported {len(self._page_classes)} pages")
        failed_imports = self.importer.get_failed_imports()
        if failed_imports:
            print(f"Failed to import {len(failed_imports)} pages:")
            for error in failed_imports:
                print(f"  - {error}")

    def create_page(self, index: int, page) -> ToolBoxPage:
        """根据索引创建页面（保持原有接口）"""
        if not self._initialized:
            self.initialize()

        page_keys = sorted(self._page_classes.keys())
        if 0 <= index < len(page_keys):
            page_key = page_keys[index]
            return self.create_page_by_key(page_key, page)
        else:
            raise ValueError(f"Page index {index} out of range")

    def create_page_by_key(self, key: str, page) -> ToolBoxPage:
        """根据key创建页面"""
        if not self._initialized:
            self.initialize()

        # 检查缓存
        cache_key = f"{key}_{id(page)}"
        if cache_key in self._page_instances:
            return self._page_instances[cache_key]

        # 创建新实例
        if key in self._page_classes:
            page_class = self._page_classes[key]
            instance = page_class(page)
            self._page_instances[cache_key] = instance
            return instance
        else:
            raise ValueError(f"Page key '{key}' not found")

    def get_available_pages(self) -> List[str]:
        """获取所有可用的页面key"""
        if not self._initialized:
            self.initialize()
        return list(self._page_classes.keys())

    def get_page_config(self, key: str) -> Dict[str, Any]:
        """获取页面配置"""
        return PageConfig.PAGE_MODULES.get(key, {})


# 使用示例
def main():
    # 方法1: 使用配置文件方式
    print("=== 使用配置文件方式 ===")
    factory = EnhancedPageFactory()
    factory.initialize("config")

    # 原有的调用方式仍然有效
    try:
        page1 = factory.create_page(0, None)  # 第一个页面
        page2 = factory.create_page_by_key("excel_split_v2", None)  # 按key创建
        print(f"Created pages: {type(page1).__name__}, {type(page2).__name__}")
    except Exception as e:
        print(f"Error creating pages: {e}")

    # 方法2: 使用目录扫描方式
    print("\n=== 使用目录扫描方式 ===")
    factory2 = EnhancedPageFactory()
    factory2.initialize("scan")
    available_pages = factory2.get_available_pages()
    print(f"Available pages: {available_pages}")

    # 方法3: 使用自动发现方式（需要在页面类上添加装饰器）
    print("\n=== 使用自动发现方式 ===")
    factory3 = EnhancedPageFactory()
    factory3.initialize("auto")


# 在你的页面文件中使用自动注册装饰器
# 例如在 page/excel_split_v2.py 中：
"""
@auto_register_page(
    key="excel_split_v2",
    label="Excel文件拆分工具",
    icon="SPLITSCREEN_OUTLINED",
    selected_icon="SPLITSCREEN",
    order=2
)
class ExcelSplitPageV2(ToolBoxPage):
    def gui(self):
        return "Excel Split Page"
"""


# 配置文件方式的外部配置示例
def load_from_json_config():
    """从JSON配置文件加载页面配置"""
    import json

    config_example = {
        "pages": {
            "excel_split_v2": {
                "module": "page.excel_split_v2",
                "class": "ExcelSplitPageV2",
                "label": "Excel文件拆分工具",
                "icon": "SPLITSCREEN_OUTLINED",
                "selected_icon": "SPLITSCREEN",
                "order": 2
            },
            "odap_formater": {
                "module": "page.odap_formater",
                "class": "ODAPFormater",
                "label": "智数平台工具",
                "icon": "LOCAL_GAS_STATION_OUTLINED",
                "selected_icon": "LOCAL_GAS_STATION",
                "order": 1
            }
        }
    }

    # 可以保存到 pages_config.json 文件
    # with open('pages_config.json', 'w') as f:
    #     json.dump(config_example, f, indent=2)

    return config_example


if __name__ == "__main__":
    main()