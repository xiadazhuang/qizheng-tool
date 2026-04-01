"""
四余计算：紫炁/月孛/罗睺/计都
四余不是真实星体，是月亮轨道上的特殊点位
"""
import swisseph as swe
from typing import Dict

# 紫炁计算基准儒略日：1280年12月14日 1:29:36 UTC
# 计算方式：swe.julday(1280, 12, 14, 1 + 29/60 + 36/3600)
_JD_EPOCH_ZIQI = 2188918.5622222223


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
    计算紫炁
    
    算法来源：《授时历》
    基准：1280年12月14日 1:29:36 UTC，紫气位于女宿2度（似黄经制）
    周期：28年绕天球一周（360度）
    每年移动：13.050460度（古度）
    每天移动：13.050460/365.2425 度（古度）
    
    宿度系统（从角宿1°起，授时历28宿黄道宿度）：
    角:0°, 亢:12.87°, 氐:22.43°, 房:38.83°, 心:44.31°, 尾:50.58°, 箕:68.53°,
    斗:78.12°, 牛:101.59°, 女:108.49°, 虚:119.61°, 危:128.62°, 室:144.57°, 壁:162.89°,
    奎:172.23°, 婁:190.10°, 胃:202.46°, 昴:218.27°, 毕:229.35°, 觜:245.85°, 参:245.90°,
    井:258.08°, 鬼:289.11°, 柳:291.22°, 星:304.22°, 张:310.53°, 翼:328.32°, 軫:348.41°
    
    注意：古度1度 = 360/365.25 ≈ 0.9856现代度
    紫气28年走完全部28宿 = 28×13.050460 = 365.41 ≈ 360古度 ≈ 360现代度
    """
    # 基准儒略日：1280年12月14日 1:29:36 UTC
    JD_EPOCH = _JD_EPOCH_ZIQI
    
    # 女宿起点在累积宿度（古度）
    NÜ_START = 108.49  # 女宿在28宿中的累积起点（古度）
    DEGREE_IN_STAR = 2.0  # 基准位置：女宿2度
    ANNUAL_DEGREE = 13.050460  # 每年移动（古度）
    DAILY_DEGREE = ANNUAL_DEGREE / 365.2425  # 每天移动（古度）
    
    # 基准位置：女宿起点 + 女宿内2度 = 女宿108.49度处的2度位置
    epoch_pos = NÜ_START + DEGREE_IN_STAR  # 古度
    
    days_elapsed = jd - JD_EPOCH
    total_ancient_deg = epoch_pos + days_elapsed * DAILY_DEGREE
    
    # 换算为现代360度制（古度 × 360/365.25）
    modern_deg = (total_ancient_deg * (360.0 / 365.25)) % 360.0
    
    return modern_deg


def calculate_four_remnants(jd: float) -> Dict[str, float]:
    """计算四余（罗睺/计都/月孛/紫炁）"""
    results = {}
    results["luohou"] = calculate_luohou(jd)
    results["jitu"] = calculate_jitu(jd)
    results["yuebo"] = calculate_yuebo(jd)
    results["ziqi"] = calculate_ziqi(jd)
    return results
