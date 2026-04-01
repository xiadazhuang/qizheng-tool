"""
JSON 输出格式化
"""
import json
from typing import Dict, Any


def to_json(data: Dict[str, Any], indent: int = 2) -> str:
    """
    将命盘数据格式化为JSON
    
    Args:
        data: 命盘数据
        indent: 缩进空格数
    
    Returns:
        str: 格式化的JSON字符串
    """
    return json.dumps(data, ensure_ascii=False, indent=indent)


def to_compact_json(data: Dict[str, Any]) -> str:
    """
    将命盘数据格式化为紧凑JSON（无缩进）
    """
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def format_bazi(bazi: dict) -> str:
    """
    格式化八字输出
    
    Example:
        庚午 / 乙酉 / 壬子 / 癸卯
    """
    return f"{bazi['year']} / {bazi['month']} / {bazi['day']} / {bazi['hour']}"


def format_degree(degree: float) -> str:
    """
    格式化黄道度数输出
    
    Example:
        225.5 -> "225°30'"
    """
    d = int(degree)
    m = int((degree - d) * 60)
    return f"{d}°{m:02d}'"
