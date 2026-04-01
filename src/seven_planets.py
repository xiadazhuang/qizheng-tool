"""
七政计算：日月金水木火土
"""
import swisseph as swe
from typing import Dict


# 七政对应的 pyswisseph 常量
SEVEN_PLANETS = {
    "sun": swe.SUN,      # 日
    "moon": swe.MOON,    # 月
    "venus": swe.VENUS,  # 金星（太白）
    "mercury": swe.MERCURY,  # 水星（辰星）
    "jupiter": swe.JUPITER,  # 木星（岁星）
    "mars": swe.MARS,    # 火星（荧惑）
    "saturn": swe.SATURN,  # 土星（镇星）
}


def calculate_seven_planets(jd: float) -> Dict[str, float]:
    """
    计算七政在黄道上的度数
    
    Args:
        jd: Julian Day（儒略日）
    
    Returns:
        dict: {星曜名: 黄道度数}
    """
    results = {}
    for name, const in SEVEN_PLANETS.items():
        pos, _ = swe.calc_ut(jd, const)
        # pos 是 tuple，第一个元素是黄道经度
        results[name] = pos[0] if isinstance(pos, tuple) else pos
    return results


def get_chinese_name(name: str) -> str:
    """获取七政的中文名称"""
    names = {
        "sun": "日",
        "moon": "月",
        "venus": "金",
        "mercury": "水",
        "jupiter": "木",
        "mars": "火",
        "saturn": "土",
    }
    return names.get(name, name)
