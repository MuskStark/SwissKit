# Swiss Kit 官方文档

## 项目背景

SwissKit项目孵化于作者日常工作所开发的效率工具箱，因一些不可抗力作者决定放弃原效率工具箱的开发工作，在剔除非泛性工具后决定基于
**GUN AGPL v3.0**开源协议进行开源。这也是为什么首个开源版本号从``v0.2.1``开始的原因。

## 安装项目

### 一、从源码构建

#### 1.克隆项目至本地

```bash
git clone https://github.com/MuskStark/SwissKit.git
cd ~/SwissKit
```

#### 2.安装项目依赖

```bash
uv sync
```

项目使用uv作为包管理器，如何安装与使用请参考uv[官方文档](https://docs.astral.sh/uv/)

3.构建应用

- macOS

```
flet build macos -v
```

[MacOS打包文档](https://flet.dev/docs/publish/macos/).

- Linux

```
flet build linux -v
```

[Linux打包文档](https://flet.dev/docs/publish/linux/).

- Windows

```
flet build windows -v
```

[Windows打包文档](https://flet.dev/docs/publish/windows/)

### 二、从Release界面直接下载

目前项目仅构建``Windows``平台的应用程序[Release Page](https://github.com/MuskStark/SwissKit/releases)，后续将会支持
``MacOS``与``Linux``平台

## SwissKit功能介绍

### 一、Excel拆分功能

使用Excel拆分功能需要先选择待拆分Excel文件（**文件仅支持.xlsx**，主要不想背负太多技术债）与最终文件拆分输出的文件夹路径。完成选择后点击
``解析后拆分``，待完成解析后将显示拆分选项。

![Excel拆分工具界面](./images/excelSplit/1.png)

#### 1.Excel基本拆分

![](./images/excelSplit/2.png)

- 支持将Excel中的Sheet页拆分成单个Excel文件；
- 支持根据选定的Sheet与列对Excel进行拆分

> **基本拆分下不支持任何包含复杂表头的Excel拆分**

#### 1.Excel高级拆分

> **高级拆分主要实现了多Sheet页同时拆分至结果文件中**

- 单一表头拆分模式

![](./images/excelSplit/3.png)

在该模式下，仅需选择需拆分的Sheet页，通过点击``获取可拆分列``按钮后可选择所选Sheet页中同名列进行拆分

- 复杂表头拆分模式

![](./images/excelSplit/4.png)

在该模式下，通过填写配置拆分规则，工具将根据配置情况对Excel进行拆分

### 二、Email效率工具

#### 1.Email群发

文档建设中

#### 2.Email地址及分组维护

##### 2.1 新增分组信息

文档建设中

## 更新日志

### [0.3.0](https://github.com/MuskStark/SwissKit/tree/v0.3.0)

新增

- 新增基于标签分组的邮件群发工具

### [0.2.2.2](https://github.com/MuskStark/SwissKit/tree/v0.2.2.2)

BugFix

- 修复以00开头的单元格值在拆分后丢失00的问题

### [0.2.2.1](https://github.com/MuskStark/SwissKit/tree/v0.2.2.1)

BugFix

- 修复仅复杂Excel拆分后可打开拆分文件输出文件夹的问题

### [0.2.2](https://github.com/MuskStark/SwissKit/tree/v0.2.2)

新增

- 支持在完成Excel文件拆分后打开拆分文件所在文件夹

BugFix

- 修复当Excel拆分列单元格中包含"/"时导致的文件路径解析异常的问题

### [0.2.1](https://github.com/MuskStark/SwissKit/tree/v0.2.1)

新增

- 支持为Excel文件增加英文列
- 支持Excel文件复杂查分
- 支持更具Excel生成Sql查询值
