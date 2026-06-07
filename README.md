# lrc-to-srt-converter
A lightweight, zero-dependency Python script to convert LRC lyrics to SRT subtitles. / 一个轻量、零依赖的 LRC 转 SRT 字幕 Python 脚本，支持双击批量转换、多编码自适应与智能时间轴优化。

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ 特性 (Features)

- 📦 **零第三方依赖 (Zero Dependencies)**：完全基于 Python 标准库（`re`, `argparse`, `pathlib`, `sys`）实现，下载即可运行。
- 🔄 **双运行模式 (Dual Modes)**：
  - **便捷批量转换（双击即用）**：不带任何参数运行时，脚本会自动扫描并批量转换**当前工作目录**下的所有 `.lrc` 文件，对不熟悉命令行的用户极度友好。
  - **高级命令行模式（CLI）**：支持在终端指定输入文件路径及自定义输出 `.srt` 文件路径。
- 🔤 **多编码鲁棒性 (Robust Encoding)**：顺序尝试 `utf-8`、`gbk`、`gb18030`、`utf-16` 等多种常见编码读取源文件，彻底告别歌词中文字符集乱码问题。
- ⏱️ **智能时间轴处理 (Smart Timeline)**：
  - **防间奏冗余**：当两句歌词之间存在长段纯音乐间奏时（默认大于 15 秒），会自动提前截止当前字幕，防止其长时间滞留屏幕。
  - **末句默认持续**：最后一句歌词自动补充默认持续时间（5 秒）。
  - **防零时差冲突**：若 LRC 出现异常导致起止时间相同时，自动进行 2 秒补偿，确保字幕顺利渲染。
- 🔗 **多标签重线性化 (Multi-tag Alignment)**：完美支持单行包含多个时间标签的 LRC 文件（例如副歌重复段落），脚本会自动对所有时间点进行全局排序。
- 🪟 **Windows 优化 (Windows Optimized)**：在 Windows 环境下双击运行时，程序结束后会自动等待回车，防止命令行窗口瞬间闪退导致无法查看日志。

## 🛠️ 环境要求 (Requirements)

- **Python 版本**：兼容 Python 3.11, 3.12, 3.13, 3.14+ （使用标准库，无需额外执行 `pip install`）

## 🚀 使用方法 (Usage)

### 方法一：快捷批量转换（推荐）
1. 将本脚本（例如命名为 `lrc_converter.py`）保存并放入你存放歌词 `.lrc` 文件的文件夹中。
2. **直接双击运行** 脚本（或者在终端中切换到该目录并执行 `python lrc_converter.py`）。
3. 脚本会自动完成当前文件夹下所有 `.lrc` 文件的转换，输出同名 `.srt` 文件。

### 方法二：命令行指定文件转换
如果你希望将脚本嵌入到自动化工作流中，或指定转换特定路径下的文件：

```bash
# 转换单个文件，默认在同目录下生成同名的 .srt 文件
python lrc_converter.py "路径/到/你的/歌词.lrc"

# 转换单个文件并指定输出路径
python lrc_converter.py "路径/到/你的/歌词.lrc" -o "指定输出/字幕文件.srt"
```

## ⚙️ 核心技术细节 (Technical Details)

- **毫秒容错**：兼容 LRC 文件中毫秒部分为 1 位（十分之一秒）、2 位（百分之一秒）及 3 位（千分之一秒）或超长截取的所有标准/非标准写法。
- **元数据清洗**：自动过滤诸如 `[ti:歌名]`、`[ar:歌手]`、`[al:专辑]`、`[by:制作人]` 等非歌词文本标签，保证生成的 SRT 字幕无杂质。
- **空歌词清屏处理**：自动识别 LRC 中用来清屏的空时间轴标签（即带时间戳但文本为空的行），不会将其作为独立空字幕块输出，确保 SRT 语法标准。

## 📄 开源许可 (License)

本项目基于 [MIT License](LICENSE) 开源协议。您可以自由地复制、修改、分发和商业化使用。
