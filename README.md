# Swiss Kit 官方文档

## 项目背景

SwissKit项目孵化于作者日常工作所开发的效率工具箱，因一些不可抗力作者决定放弃原效率工具箱的开发工作，在剔除非泛性工具后决定基于**GUN AGPL v3.0**开源协议进行开源。这也是为什么首个开源版本号从``v0.2.1``开始的原因。

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

目前项目仅构建``Windows``平台的应用程序[Release Page](https://github.com/MuskStark/SwissKit/releases)，后续将会支持``MacOS``与``Linux``平台

## SwissKit功能介绍
[SwissKit官方文档](https://muskstark.github.io/SwissKit)
