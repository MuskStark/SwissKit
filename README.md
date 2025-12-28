# SwissKit 瑞士军刀工具箱

<div align="center">

![SwissKit Logo](src/assets/icon.png)

**一个基于 Python 和 Flet 的跨平台桌面应用程序**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flet](https://img.shields.io/badge/Flet-0.80.0-blue.svg)](https://flet.dev/)
[![License](https://img.shields.io/badge/License-GNU%20AGPL%20v3.0-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/MuskStark/SwissKit.svg)](https://github.com/MuskStark/SwissKit/stargazers)

</div>

## 📋 项目简介

SwissKit（瑞士军刀工具箱）是一个基于 **Python 3.11+** 和 **Flet 0.80.0** 开发的跨平台桌面应用程序。项目孵化于作者日常工作开发的效率工具箱，现基于 **GNU AGPL v3.0** 开源协议进行开源。

### ✨ 当前版本
- **SwissKit**: v0.3.3
- **Flet**: 0.80.0 (2025年12月最新版本)
- **Python**: 3.11+
- **开发语言**: Python + TypeScript (Flet)
- **许可证**: GNU AGPL v3.0

## 🛠️ 技术栈

- **UI框架**: [Flet 0.80.0](https://flet.dev/) - 现代Python UI框架
- **数据处理**: pandas, openpyxl
- **数据库**: Peewee ORM + SQLite
- **包管理器**: uv (高性能Python包管理器)
- **其他依赖**: pypinyin, python-levenshtein, requests, pyyaml

## 📦 系统要求

- **Python**: 3.11 或更高版本
- **操作系统**: macOS 10.15+, Linux (Ubuntu 18.04+), Windows 10+
- **包管理器**: uv (推荐) 或 pip
- **内存**: 最少 512MB RAM
- **磁盘空间**: 至少 200MB 可用空间

## 🚀 快速开始

### 方法一：从源码构建

#### 1. 克隆项目
```bash
git clone https://github.com/MuskStark/SwissKit.git
cd SwissKit
```

#### 2. 安装依赖
```bash
# 推荐使用 uv (高性能包管理器)
uv sync

# 或使用传统 pip
pip install -r requirements.txt
```

#### 3. 运行应用
```bash
# 开发模式运行
uv run flet run src/main.py

# 或使用传统的 flet 命令
flet run src/main.py
```

#### 4. 构建应用

**macOS**
```bash
uv run flet build macos -v
```

**Linux**
```bash
uv run flet build linux -v
```

**Windows**
```bash
uv run flet build windows -v
```

### 方法二：直接下载

📥 访问 [Release 页面](https://github.com/MuskStark/SwissKit/releases) 下载预编译的应用程序

- ✅ Windows 10/11 (x64)
- ✅ macOS 11+ (Intel/Apple Silicon)
- ✅ Linux (Ubuntu 18.04+)

## 🏗️ 项目架构

```
SwissKit/
├── src/
│   ├── main.py                 # 应用入口点
│   ├── assets/                 # 静态资源
│   │   ├── config.toml         # 应用配置
│   │   ├── icon.png           # 应用图标
│   │   └── data/              # 数据文件
│   └── package/               # 主要代码包
│       ├── components/        # UI组件
│       ├── database/          # 数据库相关
│       ├── pages/             # 页面和功能
│       │   ├── page/          # 具体功能页面
│       │   │   ├── email/     # 邮件工具
│       │   │   ├── excel/     # Excel工具
│       │   │   └── odap_formater.py # ODAP格式化
│       │   └── toolbox_page.py # 工具箱基类
│       └── util/              # 工具类
├── docs/                      # 项目文档
├── pyproject.toml             # 项目配置
├── IFLOW.md                   # 开发指南
└── README.md                  # 项目说明
```

## 🧰 核心功能

### 1. 📧 邮件工具 (Email)
- **邮件发送**: 批量邮件发送功能
- **邮件分组**: 联系人分组管理
- **邮件设置**: SMTP 配置和邮件模板
- **发送日志**: 邮件发送记录和状态跟踪

### 2. 📊 Excel 工具 (Excel Split)
- **智能拆分**: 按Sheet页或列值智能拆分Excel文件
- **格式保持**: 保持原文件的格式和样式
- **批量处理**: 支持多文件批量操作
- **跨平台**: 支持Windows、macOS、Linux文件系统

### 3. 🌍 ODAP 格式化器 (ODAP Formatter)
- **双语表头**: 为Excel文件添加中英文双语表头
- **智能翻译**: 基于拼音和词典的智能翻译
- **格式优化**: 自动优化日期和数值格式
- **批量转换**: 支持批量文件处理

### 4. 🔍 搜索工具 (ODAP Search Value)
- **数据搜索**: 在Excel文件中快速搜索特定值
- **智能匹配**: 支持模糊匹配和相似度算法
- **结果导出**: 搜索结果可导出为Excel或CSV

## 💻 开发环境搭建

### 1. 环境要求
```bash
# Python 3.11+
python --version

# 安装 uv 包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 项目设置
```bash
# 克隆项目
git clone https://github.com/MuskStark/SwissKit.git

# 进入项目目录
cd SwissKit

# 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows
```

### 3. 运行开发服务器
```bash
# 启动开发模式
uv run flet run src/main.py

# 开启热重载 (推荐)
uv run flet run src/main.py --reload
```

## 🔧 Flet 0.80.0 升级说明

⚠️ **重要**: SwissKit 已于 2025年12月 升级到 Flet 0.80.0，此版本包含破坏性更改。

### 主要变更
1. **事件类型变更**:
   - `ft.FilePickerResultEvent` → `ft.ControlEvent`
   
2. **FilePicker API 变更**:
   - 移除了 `on_result` 参数
   - 使用新的事件处理机制

### 升级影响
- ✅ **完全兼容**: 所有功能正常工作
- ✅ **性能提升**: Flet 0.80.0 性能显著提升
- ✅ **新功能**: 支持更多现代UI特性
- ✅ **跨平台**: 更好的跨平台兼容性

### 兼容性
- **Python**: 3.11 - 3.13 ✅
- **macOS**: 10.15+ ✅
- **Windows**: 10+ ✅
- **Linux**: Ubuntu 18.04+ ✅

## 📚 文档

- 📖 [IFLOW.md](./IFLOW.md) - 详细的开发指南
- 🌐 [官方文档](https://muskstark.github.io/SwissKit) - 在线文档
- 📋 [API 文档](./docs/) - 内部API参考

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南
1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送分支: `git push origin feature/AmazingFeature`
5. 开启 Pull Request

### 开发规范
- 遵循 PEP 8 Python 编码规范
- 使用类型注解 (Type Hints)
- 添加适当的日志记录
- 确保跨平台兼容性

## 📄 许可证

本项目采用 **GNU AGPL v3.0** 许可证。详情请参见 [LICENSE](LICENSE) 文件。

```
SwissKit - Swiss Army Knife Toolkit
Copyright (C) 2025 by Summer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
```

## 📞 联系我们

- **作者**: Summer (gitman@outlook.sg)
- **项目地址**: [https://github.com/MuskStark/SwissKit](https://github.com/MuskStark/SwissKit)
- **问题反馈**: [GitHub Issues](https://github.com/MuskStark/SwissKit/issues)
- **功能建议**: [GitHub Discussions](https://github.com/MuskStark/SwissKit/discussions)

## 🙏 致谢

感谢以下开源项目:
- [Flet](https://flet.dev/) - 现代化的Python UI框架
- [Pandas](https://pandas.pydata.org/) - 强大的数据处理库
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel文件处理
- [Peewee](https://peewee-orm.com/) - 轻量级ORM
- [uv](https://docs.astral.sh/uv/) - 高性能Python包管理器

---

<div align="center">

⭐ 如果这个项目对您有帮助，请给我们一个 Star！ ⭐

[⬆️ 回到顶部](#swisskit-瑞士军刀工具箱)

</div>
