#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LRC to SRT Converter
兼容版本: Python 3.11, 3.12, 3.13, 3.14
此脚本用于将 .lrc 歌词文件转换为标准的 .srt 字幕文件。
使用全标准库实现，无需安装第三方依赖。
"""

import re
import argparse
from pathlib import Path
import sys

def parse_time(m_str: str, s_str: str, ms_str: str) -> int:
    """
    将 LRC 的时间部分解析为总毫秒数
    """
    m = int(m_str)
    s = int(s_str)
    ms = 0
    if ms_str:
        # LRC中的毫秒可能是1位(十分之一秒)、2位(百分之一秒)或3位(千分之一秒)
        if len(ms_str) == 1:
            ms = int(ms_str) * 100
        elif len(ms_str) == 2:
            ms = int(ms_str) * 10
        elif len(ms_str) == 3:
            ms = int(ms_str)
        else:
            # 如果超过3位，截取前3位
            ms = int(ms_str[:3])
    
    return (m * 60 * 1000) + (s * 1000) + ms

def format_srt_time(ms: int) -> str:
    """
    将总毫秒数格式化为 SRT 格式的时间戳 HH:MM:SS,mmm
    """
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def convert_lrc_to_srt(lrc_text: str, default_duration_ms: int = 5000, max_gap_ms: int = 15000) -> str:
    """
    核心转换逻辑
    :param lrc_text: LRC文件的纯文本内容
    :param default_duration_ms: 最后一句歌词的默认持续时间（毫秒）
    :param max_gap_ms: 句子之间的最大间隔，如果下一句在很久之后，提前结束当前字幕（毫秒）
    """
    # 匹配时间标签: [mm:ss] 或 [mm:ss.xx] 或 [mm:ss.xxx]
    time_tag_pattern = re.compile(r'\[(\d{2,}):(\d{2})(?:\.(\d+))?\]')
    
    events = []
    
    for line in lrc_text.splitlines():
        line = line.strip()
        if not line:
            continue
            
        # 查找当前行的所有时间标签
        tags = time_tag_pattern.findall(line)
        if not tags:
            # 可能是 [ti:歌名], [ar:歌手] 等元数据，直接跳过
            continue 
            
        # 剔除所有时间标签，剩下的就是歌词文本
        text = time_tag_pattern.sub('', line).strip()
        
        for tag in tags:
            ms = parse_time(tag[0], tag[1], tag[2])
            events.append((ms, text))
            
    # 按照时间进行排序（因为有的歌词会在同一行写多个时间标签，例如副歌重复）
    events.sort(key=lambda x: x[0])
    
    srt_lines = []
    subtitle_index = 1
    event_count = len(events)
    
    for i in range(event_count):
        start_time, text = events[i]
        
        # 如果歌词为空，一般是用来清屏的时间轴标签，跳过它作为独立字幕
        if not text:
            continue
            
        # 计算该行字幕的结束时间
        if i + 1 < event_count:
            next_time = events[i+1][0]
            # 避免单句字幕停留在屏幕上的时间过长（如较长的纯音乐间奏）
            if next_time - start_time > max_gap_ms:
                end_time = start_time + max_gap_ms
            else:
                end_time = next_time
        else:
            # 最后一句歌词使用默认持续时间
            end_time = start_time + default_duration_ms
            
        # 如果开始和结束时间完全一样（通常不应该发生，除非LRC时间轴有错误）
        if end_time == start_time:
            end_time += 2000 # 补偿2秒
            
        # 构建SRT区块
        srt_lines.append(str(subtitle_index))
        srt_lines.append(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}")
        srt_lines.append(text)
        srt_lines.append("") # 两个字幕区块之间的空行
        
        subtitle_index += 1
        
    return "\n".join(srt_lines)

def read_lrc_file(file_path: Path) -> str:
    """
    尝试以不同的编码格式读取 LRC 文件，解决中文字符乱码问题
    """
    encodings_to_try = ['utf-8', 'gbk', 'gb18030', 'utf-16']
    
    for enc in encodings_to_try:
        try:
            return file_path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
            
    # 如果所有常规编码都失败，强行使用utf-8并忽略错误
    return file_path.read_text(encoding='utf-8', errors='ignore')

def process_file(input_path: Path, output_path: Path = None):
    """
    处理单个文件的转换流程
    """
    if not output_path:
        output_path = input_path.with_suffix('.srt')
    try:
        lrc_text = read_lrc_file(input_path)
        srt_text = convert_lrc_to_srt(lrc_text)
        output_path.write_text(srt_text, encoding='utf-8')
        print(f"成功: '{input_path.name}' -> '{output_path.name}'")
    except Exception as e:
        print(f"转换 '{input_path.name}' 时出现错误: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="LRC 到 SRT 字幕格式转换器 (Python 3.11-3.14兼容)")
    # 使用 nargs='?' 允许 input 为空，这样直接双击运行也不会报错
    parser.add_argument("input", type=str, nargs='?', help="输入的 .lrc 文件路径 (若不提供，则自动处理当前目录所有LRC文件)")
    parser.add_argument("-o", "--output", type=str, help="输出的 .srt 文件路径 (可选，默认与输入文件同名)", default=None)
    
    args = parser.parse_args()
    
    if args.input:
        # 命令行指定了单个文件时的逻辑
        input_path = Path(args.input)
        if not input_path.exists() or not input_path.is_file():
            print(f"错误: 找不到输入文件 '{input_path}'", file=sys.stderr)
            sys.exit(1)
            
        if input_path.suffix.lower() != '.lrc':
            print(f"警告: 输入文件可能不是标准 LRC 文件 (后缀为 {input_path.suffix})")
            
        output_path = Path(args.output) if args.output else None
        process_file(input_path, output_path)
    else:
        # 没有指定参数时（例如直接双击运行），批量处理当前目录所有 .lrc 文件
        current_dir = Path.cwd()
        lrc_files = list(current_dir.glob('*.lrc'))
        
        if not lrc_files:
            print("当前目录下没有找到任何 .lrc 文件。")
            print("使用说明: 请将此脚本(.py)放入包含歌词(.lrc)的文件夹中，然后直接双击运行。")
        else:
            print(f"发现 {len(lrc_files)} 个 .lrc 文件，开始批量转换...\n")
            for lrc_path in lrc_files:
                process_file(lrc_path)
            print("\n批量转换完成！")
        
        # 防止在 Windows 系统下双击运行后终端窗口瞬间关闭
        if sys.platform == 'win32':
            input("\n按回车键退出...")

if __name__ == "__main__":
    main()
