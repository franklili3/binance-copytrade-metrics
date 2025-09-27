# Windows + Python 3.13 兼容性问题说明

## 问题描述

在 Windows 系统上使用 Python 3.13 运行 Playwright 时，会出现以下错误：

```
NotImplementedError
```

这是由于 Python 3.13 在 Windows 上对 asyncio 子进程实现进行了更改，导致 Playwright 无法创建子进程来启动浏览器。

## 解决方案

### 方案一：降低 Python 版本（推荐）

将 Python 版本降低到 3.11 或 3.12：

1. 卸载 Python 3.13
2. 安装 Python 3.11 或 3.12
3. 重新安装项目依赖

### 方案二：使用 Docker（推荐用于生产环境）

使用 Docker 容器运行项目，避免本地环境问题：

```bash
# 构建镜像
docker build -t binance-copytrade-metrics .

# 运行容器
docker run binance-copytrade-metrics
```

### 方案三：部署到阿里云函数计算

项目已配置好阿里云函数计算部署支持，可以直接部署到云端运行：

```bash
# 部署到阿里云函数计算
s deploy
```

## 本地开发建议

对于本地开发，建议使用 Python 3.11 或 3.12 环境，以确保与 Playwright 的兼容性。

## 已修复的其他问题

除了 Python 3.13 兼容性问题外，我们还修复了 scrapy-playwright 库的一个小问题：

在 `scrapy_playwright/handler.py` 文件中，`_maybe_launch_browser` 方法访问 `self.browser_type` 属性时可能出错，已通过直接从 `self.playwright` 对象获取浏览器类型修复。