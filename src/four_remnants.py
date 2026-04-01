"""
四余计算：紫炁/月孛/罗睺/计都
四余不是真实星体，是月亮轨道上的特殊点位
"""
import swisseph as swe
from typing import Dict


def calculate_luohou(jd: float) -> float:
    """
    计算罗睺（月亮升交点）
    罗睺 = 月亮轨道与黄道的升交点（北交点）
    """
    # TRUE_NODE = 月亮真升交点
    pos, _ = swe.calc_ut(jd, swe.TRUE_NODE)
    pos = pos[0] if isinstance(pos, tuple) else pos
    return pos % 360


def calculate_jitu(jd: float) -> float:
    """
    计算计都（月亮降交点）
    计都 = 罗睺对面（+180°）
    """
    luohou = calculate_luohou(jd)
    return (luohou + 180) % 360


def calculate_yuebo(jd: float) -> float:
    """
    计算月孛（月亮远地点）
    月孛 = 白道椭圆长轴端点
    """
    # MEAN_APOG = 月亮远地点平均距离
    pos, _ = swe.calc_ut(jd, swe.MEAN_APOG)
    pos = pos[0] if isinstance(pos, tuple) else pos
    return pos % 360


def calculate_ziqi(jd: float) -> float:
    """
    计算紫炁（木星余气）
    紫炁约9年绕天球一周（与木星周期相关）
    具体算法待研究
    """
    # TODO: 紫炁的精确算法
    # 紫炁 = (木星位置 * 修正系数) mod 360
    # 需要参考文献确定修正系数
    pass


def calculate_four_remnants(jd: float) -> Dict[str, float]:
    """计算四余"""
    results = {}
    results["luohou"] = calculate_luohou(jd)
    results["jitu"] = calculate_jitu(jd)
    results["yuebo"] = calculate_yuebo(jd)
    results["ziqi"] = calculate_ziqi(jd) if calculate_ziqi(jd) else None
    return results
