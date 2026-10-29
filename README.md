# 必应壁纸下载器 (Bing Wallpaper Downloader)

一个基于 Python + tkinter 的桌面小工具，用于**批量下载必应（Bing）每日壁纸**。支持按日期范围筛选、选择分辨率、多线程高速下载，并自动获取壁纸元数据。

> 版本：v1.5 ｜ 图形界面（GUI）

## ✨ 功能特性

- 📆 **日期范围选择**：可下载从 2018-09-11 至今的必应壁纸（更早的仅支持 1080P）。
- 🖼️ **分辨率选择**：原图 / 4K(3840×2160) / 2K(2560×1440) / 1080P(1920×1080) / 自定义分辨率。
- 🚀 **多线程下载**：线程数 1–32 可调（默认 8），大幅提升下载速度。
- 💾 **自动元数据**：缺少 `Bing_zh-CN_all.json` 时程序会自动从 CDN 下载并更新。
- 📂 **按年份归档**：下载的图片按年份自动分文件夹保存，已存在的文件自动跳过。

## 📦 安装与运行

需要 **Python 3** 环境（tkinter 为 Python 内置模块）。

```bash
# 1. 安装第三方依赖（仅需 requests）
pip install requests

# 2. 运行主程序
python bing壁纸下载器.py
```

运行后会弹出图形界面：选择日期范围 → 选择分辨率 → 选择下载文件夹 → 点击「开始下载壁纸」。

## 🛠 打包为 exe（可选）

项目已附带 PyInstaller 配置（`bing壁纸下载器.spec`）。一键打包命令：

```bash
pyinstaller -w --onefile --icon=1.ico bing壁纸下载器.py
```

打包产物位于 `dist/` 目录（已被 `.gitignore` 忽略，不纳入版本库）。

## 📁 项目结构

| 文件 | 说明 |
| --- | --- |
| `bing壁纸下载器.py` | 主程序源码（tkinter GUI） |
| `bing壁纸下载器.spec` | PyInstaller 打包配置 |
| `打包命令.txt` | 打包命令备忘 |
| `1.ico` | 程序图标 |
| `Bing_zh-CN_all.json` | 必应壁纸元数据（运行时自动更新） |

## 🔗 数据来源

壁纸元数据来自开源项目 [Zhu-junwei/bing-wallpaper-archive](https://github.com/Zhu-junwei/bing-wallpaper-archive)，
通过 jsDelivr CDN 分发：

```
https://cdn.jsdelivr.net/gh/Zhu-junwei/bing-wallpaper-archive/Bing_zh-CN_all.json
```

图片本体从 `https://www.bing.com` 官方接口下载。

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。
