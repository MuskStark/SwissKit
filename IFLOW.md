# SwissKit 项目交互指南

## 项目概述

**SwissKit（瑞士军刀工具箱）** 是一个基于 Python 和 Flet 框架开发的跨平台桌面应用程序。项目起源于作者日常工作开发的效率工具箱，现基于 **GNU AGPL v3.0** 开源协议进行开源。

### 基本信息
- **当前版本**: v0.3.3
- **开发语言**: Python 3.11+
- **UI框架**: Flet 0.80.0
- **包管理器**: uv
- **许可证**: GNU AGPL v3.0
- **作者**: Summer (gitman@outlook.sg)
- **项目地址**: https://github.com/MuskStark/SwissKit.git

### 技术栈
- **前端界面**: Flet (现代Python UI框架)
- **数据处理**: pandas, openpyxl
- **数据库**: Peewee ORM + SQLite
- **工具库**: 
  - pypinyin (中文拼音转换)
  - python-levenshtein (字符串相似度匹配)
  - requests (HTTP请求)
  - pyyaml (YAML配置)
  - picologging (高性能日志)

## 核心功能模块

### 1. 邮件工具 (Email)
**文件路径**: `src/package/pages/page/email/email_main.py`

**主要功能**:
- 邮件发送功能
- 邮件分组设置
- 邮件配置管理

**相关文件**:
- `src/package/pages/page/email/email_editor_page.py` - 邮件编辑器
- `src/package/pages/page/email/email_info_page_v2.py` - 邮件信息管理
- `src/package/pages/page/email/email_setting_page.py` - 邮件设置
- `src/package/database/pojo/email/` - 邮件相关数据模型

### 2. Excel工具 (Excel Split)
**文件路径**: `src/package/pages/page/excel/excel_split_v2.py`

**主要功能**:
- Excel文件智能拆分
- 支持多种拆分模式：
  - 无合并单元格单一表头拆分
  - 复杂表头拆分
  - 根据Sheet页拆分
  - 根据列拆分
- 保持原文件格式选项
- 跨平台文件浏览器集成

**相关文件**:
- `src/package/pages/page/excel/excel_split_keep_format.py` - 格式保持拆分
- `src/package/util/excel_util.py` - Excel工具类
- `src/package/components/progress_ring_components.py` - 进度指示器

### 3. ODAP格式化器 (ODAP Formatter)
**文件路径**: `src/package/pages/page/odap_formater.py`

**主要功能**:
- 为Excel文件添加英文表头
- 支持中英文双语表头
- 智能拼音转换
- 字符串相似度匹配
- 支持缩写模式

**相关文件**:
- `src/assets/data/odap/en_cn_dic.json` - 中英文对照字典
- `src/package/util/json_loader.py` - JSON加载工具

### 4. 工具箱 (ToolBox)
**基类**: `src/package/toolbox_page.py`
**工厂模式**: `src/package/pages/page_facroty.py`

## 项目架构

### 目录结构
```
src/
├── main.py                 # 应用入口点
├── assets/                 # 静态资源
│   ├── config.toml         # 应用配置
│   ├── icon.png           # 应用图标
│   └── data/              # 数据文件
└── package/               # 主要代码包
    ├── components/        # UI组件
    │   ├── file_or_path_picker.py
    │   ├── multi_select_component.py
    │   ├── navigation.py
    │   ├── new_navigation.py
    │   ├── progress_ring_components.py
    │   └── search_component.py
    ├── database/          # 数据库相关
    │   ├── database_obj.py     # 数据库对象
    │   └── pojo/               # 数据模型
    ├── enums/             # 枚举定义
    ├── pages/             # 页面和功能
    │   ├── page_facroty.py     # 页面工厂
    │   ├── pages_loader.py     # 页面加载器
    │   ├── toolbox_page.py     # 工具箱基类
    │   └── page/               # 具体功能页面
    │       ├── email/          # 邮件功能
    │       ├── excel/          # Excel功能
    │       └── odap_formater.py # ODAP格式化
    └── util/              # 工具类
        ├── dataframe_util.py
        ├── excel_util.py
        ├── json_loader.py
        ├── log_util.py
        ├── path_util.py
        ├── postman.py
        ├── resource_path.py
        └── tool_util.py
```

### 核心设计模式

1. **工厂模式**: `PageFactory.create_page()` 根据索引创建不同页面
2. **抽象基类**: `ToolBoxPage` 定义工具页面的标准接口
3. **导航模式**: `navigation.navigation_gui()` 提供统一的导航界面
4. **数据库抽象**: `DataBaseObj` 统一数据库操作接口

## 构建和运行

### 环境要求
- Python 3.11+
- uv 包管理器

### 开发环境设置

1. **克隆项目**:
```bash
git clone https://github.com/MuskStark/SwissKit.git
cd SwissKit
```

2. **安装依赖**:
```bash
uv sync
```

3. **运行应用**:
```bash
uv run flet run src/main.py
```

### 构建发布版本

**macOS**:
```bash
uv run flet build macos -v
```

**Linux**:
```bash
uv run flet build linux -v
```

**Windows**:
```bash
uv run flet build windows -v
```

### 配置文件

**主配置文件**: `src/assets/config.toml`
```toml
version = '0.3.3'
special_modl = 'False'
```

## 开发规范

### 代码风格
- 遵循 PEP 8 Python 编码规范
- 使用类型注解 (Type Hints)
- 详细的日志记录 (picologging)
- 异常处理和错误恢复

### 架构原则
1. **模块化设计**: 每个功能独立封装
2. **接口抽象**: 通过抽象基类定义标准接口
3. **数据分离**: 界面逻辑与数据处理分离
4. **跨平台兼容**: 适配不同操作系统的路径和文件系统

### 数据库设计
- 使用 Peewee ORM 进行数据抽象
- SQLite 作为本地数据库
- 跨环境数据库路径自动适配
- 支持开发和生产环境切换

### 页面开发模式

1. **继承 ToolBoxPage 基类**:
```python
class YourTool(ToolBoxPage):
    def __init__(self, page: ft.Page):
        self.page = page
    
    def gui(self):
        # 返回 Flet 控件
        return ft.Column([...])
```

2. **在页面工厂中注册**:
编辑 `src/package/pages/page_facroty.py` 添加新的页面类

## 常见开发任务

### 添加新工具页面

1. **创建工具类**:
```python
# src/package/pages/page/your_tool.py
import flet as ft
from ..toolbox_page import ToolBoxPage

class YourTool(ToolBoxPage):
    def __init__(self, page: ft.Page):
        self.page = page
    
    def gui(self):
        return ft.Column([
            ft.Text("你的工具界面"),
            # 添加你的UI控件
        ])
```

2. **注册到工厂**:
编辑 `src/package/pages/page_facroty.py` 添加页面映射

3. **更新导航**:
在 `src/package/components/navigation.py` 中添加工具入口

### 数据库操作

```python
from ...database.database_obj import DataBaseObj

# 在工具类中初始化数据库
self.database = DataBaseObj()

# 创建数据表
models = [YourModel]  # 定义你的数据模型
self.database.creat_table(models)
```

### 配置文件访问

```python
import tomllib
from ...util.resource_path import resource_path

# 加载配置
with open(resource_path('assets/config.toml'), 'br') as config_file:
    config = tomllib.load(config_file)
```

### 资源文件路径

```python
from ...util.resource_path import resource_path

# 获取资源文件绝对路径
icon_path = resource_path('assets/icon.png')
```

## 故障排除

### Flet 0.80.0 迁移注意事项

⚠️ **重要**: Flet 0.80.0 包含破坏性更改，需要手动迁移。

#### 主要变更
1. **事件类型变更**:
   - `ft.FilePickerResultEvent` → `ft.ControlEvent`
   - 所有文件选择回调函数需要更新事件类型

2. **FilePicker API 变更**:
   - 移除了 `on_result` 参数
   - FilePicker 构造函数不再接受回调函数

#### 迁移步骤
1. 将所有 `FilePickerResultEvent` 替换为 `ControlEvent`
2. 移除所有 `FilePicker(on_result=...)` 调用
3. 重新同步依赖: `uv sync`

### 常见问题

1. **数据库连接问题**: 检查数据库文件路径权限
2. **文件路径问题**: 使用 `resource_path()` 和 `path_util.py` 中的工具
3. **Flet 界面问题**: 确保正确导入和使用 Flet 控件
4. **依赖问题**: 运行 `uv sync` 重新安装依赖
5. **Flet 0.80.0 迁移问题**: 检查 FilePicker 和事件类型的迁移

### 日志调试

项目使用 `picologging` 进行日志记录：
```python
from ...util.log_util import get_logger

logger = get_logger('your_module')
logger.info("调试信息")
logger.error("错误信息")
```

### 开发环境调试

1. **启用详细日志**:
```bash
uv run flet run src/main.py --debug
```

2. **数据库调试**:
检查 `database-test/` 目录下的 SQLite 文件

3. **配置文件验证**:
确保 `config.toml` 格式正确且版本号匹配

## 贡献指南

1. 遵循现有的代码结构和命名约定
2. 添加适当的日志记录
3. 处理异常和边界情况
4. 保持跨平台兼容性
5. 更新相关文档

## 许可证信息

本项目采用 **GNU AGPL v3.0** 开源许可证，详情请参考项目根目录下的 `LICENSE` 文件。

---

*最后更新时间: 2025-12-28*
*项目版本: v0.3.3*