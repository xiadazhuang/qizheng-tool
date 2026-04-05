"""
真太阳时计算模块
用于八字排盘的精确出生时间修正

真太阳时 = 北京时间 + (当地经度 - 120) × 4分钟

中国夏令时（DST）支持（1986-1991年）：
  中国于1986-1991年实行夏令时，期间出生的人，实际时间 = 北京时间 - 1小时
  具体时间区间（北京时间）为：
    1986年: 5月4日 02:00 ~ 9月13日 02:00
    1987年: 4月12日 02:00 ~ 9月12日 02:00
    1988年: 4月10日 02:00 ~ 9月11日 02:00
    1989年: 4月16日 02:00 ~ 9月16日 02:00
    1990年: 4月15日 02:00 ~ 9月15日 02:00
    1991年: 4月14日 02:00 ~ 9月14日 02:00
"""
import time
import urllib.request
import json
from typing import Optional

# Nominatim API 用户代理（必须按规范设置）
NOMINATIM_UA = "qizheng-tool/1.0 (https://github.com/qizheng-tool)"

# 中国主要城市经纬度 fallback 表（用于 API 不可用时）
CITY_COORDINATES_FALLBACK = {
    "北京": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
    "广州": (23.1291, 113.2644),
    "深圳": (22.5431, 114.0579),
    "杭州": (30.2741, 120.1551),
    "成都": (30.5728, 104.0668),
    "重庆": (29.4316, 106.9123),
    "武汉": (30.5928, 114.3055),
    "西安": (34.3416, 108.9398),
    "南京": (32.0603, 118.7969),
    "天津": (39.3434, 117.3616),
    "苏州": (31.2989, 120.5853),
    "郑州": (34.7466, 113.6253),
    "长沙": (28.2282, 112.9388),
    "沈阳": (41.8057, 123.4328),
    "青岛": (36.0671, 120.3826),
    "济南": (36.6512, 117.1201),
    "大连": (38.9144, 121.6147),
    "昆明": (25.0406, 102.7129),
    "哈尔滨": (45.8038, 126.5340),
    "长春": (43.8171, 125.3235),
    "福州": (26.0745, 119.2965),
    "厦门": (24.4798, 118.0894),
    "南宁": (22.8170, 108.3665),
    "贵阳": (26.6470, 106.6302),
    "太原": (37.8706, 112.5489),
    "兰州": (36.0611, 103.8343),
    "石家庄": (38.0428, 114.5149),
    "乌鲁木齐": (43.8256, 87.6177),
    "拉萨": (29.6500, 91.1000),
    "呼和浩特": (40.8424, 111.7492),
    "海口": (20.0444, 110.3497),
    "三亚": (18.2528, 109.5117),
    "珠海": (22.2710, 113.5767),
    "东莞": (23.0489, 113.7447),
    "宁波": (29.8683, 121.5440),
    "温州": (28.0006, 120.6994),
    "无锡": (31.4912, 120.3119),
    "佛山": (23.0218, 113.1219),
    "合肥": (31.8206, 117.2272),
    "南昌": (28.6820, 115.8579),
    "南宁": (22.8170, 108.3665),
    "东莞": (23.0489, 113.7447),
}

# 中国夏令时时间区间表（start_date, end_date 为 (month, day) 元组）
# 北京夏令时：每年 start_day 02:00 开始，end_day 02:00 结束
CHINA_DST_PERIODS = {
    1986: ((5, 4), (9, 13)),
    1987: ((4, 12), (9, 12)),
    1988: ((4, 10), (9, 11)),
    1989: ((4, 16), (9, 16)),
    1990: ((4, 15), (9, 15)),
    1991: ((4, 14), (9, 14)),
}


def is_dst_period(year: int, month: int, day: int) -> bool:
    """
    判断某日期是否在夏令时期间（中国 1986-1991）

    Args:
        year: 出生年份
        month: 出生月份（1-12）
        day: 出生日期（1-31）

    Returns:
        True 如果在夏令时期间，否则 False

    中国夏令时：每年特定日期 02:00 开始，到特定日期 02:00 结束。
    02:00 切换意味着当天 00:00-01:59 仍然按标准时间，02:00 起进入夏令时。
    为方便计算，我们以 00:00 为界：当天 00:00 起即视为夏令时生效。
    """
    if year not in CHINA_DST_PERIODS:
        return False

    (start_m, start_d), (end_m, end_d) = CHINA_DST_PERIODS[year]

    # 使用 (month, day) 元组比较日期
    # (start_m, start_d) <= (month, day) <= (end_m, end_d)
    return (start_m, start_d) <= (month, day) <= (end_m, end_d)


def get_city_coordinates(city_name: str, use_fallback: bool = True) -> tuple[float, float]:
    """
    获取城市经纬度（优先 Nominatim API，失败则用 fallback 表）

    Args:
        city_name: 城市名称，支持 "北京" 或 "北京, China"
        use_fallback: API 失败时是否使用 fallback 表

    Returns:
        (纬度, 经度) tuple

    Raises:
        ValueError: 城市查不到时抛出
    """
    # 先在 fallback 表中查找（不区分大小写）
    if use_fallback:
        for key, coords in CITY_COORDINATES_FALLBACK.items():
            if key in city_name or city_name in key:
                return coords

    # 使用 Nominatim API 查询
    query = city_name if "," in city_name else f"{city_name}, China"
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"

    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": NOMINATIM_UA})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return (lat, lon)

            # 没查到结果
            if attempt == 0:
                # 再试一次，加上 ", China" 后缀
                url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(city_name)},+China&format=json&limit=1"
                time.sleep(1.1)  # Nominatim 限速：每秒最多1个请求
                continue
            break

        except Exception as e:
            if attempt == 0:
                time.sleep(1.1)
                continue
            # API 完全失败

    # 尝试纯 fallback 查找
    if use_fallback:
        for key, coords in CITY_COORDINATES_FALLBACK.items():
            if key in city_name:
                return coords
        # 精确匹配
        if city_name in CITY_COORDINATES_FALLBACK:
            return CITY_COORDINATES_FALLBACK[city_name]

    raise ValueError(f"❌ 找不到城市「{city_name}」的经纬度，请尝试输入更详细的地址或直接提供经度（--lon）")


def calculate_true_solar_time(timezone_hour: int, lon: float) -> int:
    """
    将北京时间转换为真太阳时（向下取整到小时）

    Args:
        timezone_hour: 北京时间小时（0-23）
        lon: 出生地经度（如 87.6 乌鲁木齐，121.5 上海）

    Returns:
        真太阳时的小时数（0-23，向下取整）

    计算公式：
        真太阳时 = 北京时间 + (当地经度 - 120) × 4分钟
        修正值 = (lon - 120) × 4（分钟）

    示例：
        上海 (121.5°E) 7:00北京时间 → 7 + (121.5-120)×4/60 = 7.1h → 7时（辰时）
        乌鲁木齐 (87.6°E) 7:00北京时间 → 7 + (87.6-120)×4/60 = 4.84h → 4时（丑时）
    """
    correction_minutes = (lon - 120) * 4  # 单位：分钟
    total_hours = timezone_hour + correction_minutes / 60.0
    # 向下取整
    return int(total_hours)


def adjust_birth_hour_for_true_solar(
    birth_hour: int,
    birth_min: int,
    lon: float,
    year: int = None,
    month: int = None,
    day: int = None,
) -> tuple[int, int, dict]:
    """
    调整出生时间为真太阳时（考虑中国夏令时 1986-1991）

    处理流程：
      1. 判断是否在夏令时期间（1986-1991年，每年特定日期区间）
      2. 如果是夏令时，实际时间 = 北京时间 - 1小时（夏令时时间比真实时间快1小时）
      3. 再计算真太阳时修正

    Args:
        birth_hour: 北京时间小时（0-23）
        birth_min: 北京时间分钟（0-59）
        lon: 出生地经度
        year: 出生年（用于判断夏令时，可选）
        month: 出生月（用于判断夏令时，可选）
        day: 出生日（用于判断夏令时，可选）

    Returns:
        (调整后小时, 调整后分钟, 修正信息dict)
        修正信息包含：
          - dst_applied: bool，是否应用了夏令时修正
          - dst_minus_1h: bool，是否减了1小时（夏令时期间）
          - solar_correction_min: int，真太阳时修正分钟数
          - original_hour: int，原始输入小时
          - original_min: int，原始输入分钟
    """
    info = {
        "dst_applied": False,
        "dst_minus_1h": False,
        "solar_correction_min": 0,
        "original_hour": birth_hour,
        "original_min": birth_min,
    }

    effective_hour = birth_hour
    effective_min = birth_min

    # Step 1: 夏令时修正（1986-1991年）
    if year is not None and month is not None and day is not None:
        if is_dst_period(year, month, day):
            info["dst_applied"] = True
            info["dst_minus_1h"] = True
            # 减1小时（夏令时期间，北京时间比真实时间快1小时）
            total_mins = effective_hour * 60 + effective_min - 60
            if total_mins < 0:
                total_mins += 24 * 60
            effective_hour = total_mins // 60
            effective_min = total_mins % 60

    # Step 2: 真太阳时修正
    solar_corr = int((lon - 120) * 4)  # 真太阳时修正（分钟）
    info["solar_correction_min"] = solar_corr

    total_minutes = effective_hour * 60 + effective_min + solar_corr
    adjusted_minutes = int(total_minutes)
    adj_hour = adjusted_minutes // 60
    adj_min = adjusted_minutes % 60
    # 处理跨天（真太阳时可能跨日）
    adj_hour = adj_hour % 24

    return adj_hour, adj_min, info


if __name__ == "__main__":
    import urllib.parse

    # 测试用例
    test_cases = [
        ("上海", 121.4737, 7, 0, 2024, 5, 1),   # 非DST，7:00北京时间 → 真太阳时 ~7:06
        ("乌鲁木齐", 87.6177, 7, 0, 2024, 5, 1),  # 非DST，7:00北京时间 → 真太阳时 ~4:54（丑时！）
        ("北京", 116.4074, 12, 0, 2024, 5, 1),   # 非DST，12:00北京时间 → 真太阳时 ~11:58
        ("乌鲁木齐", 87.6177, 23, 0, 2024, 5, 1),  # 非DST，23:00北京时间 → 真太阳时 ~20:54
        # DST边界测试
        ("乌鲁木齐", 87.6177, 7, 0, 1988, 4, 10),  # DST开始日 7:00北京时间 → DST→6:00, 真太阳时 ~3:48
        ("乌鲁木齐", 87.6177, 7, 0, 1988, 4, 17),  # DST期间 7:00北京时间 → DST→6:00, 真太阳时 ~3:48
        ("乌鲁木齐", 87.6177, 7, 0, 1988, 9, 11),  # DST最后一天 7:00北京时间 → DST→6:00, 真太阳时 ~3:48
        ("乌鲁木齐", 87.6177, 7, 0, 1988, 9, 17),  # DST结束后 7:00北京时间 → 真太阳时 ~4:54
        # 非DST年份（1986年边界）
        ("乌鲁木齐", 87.6177, 7, 0, 1986, 5, 3),  # DST前 7:00北京时间 → 真太阳时 ~4:54
        ("乌鲁木齐", 87.6177, 7, 0, 1986, 5, 4),  # DST首日 7:00北京时间 → DST→6:00, 真太阳时 ~3:48
        ("乌鲁木齐", 87.6177, 7, 0, 1986, 9, 14),  # DST末日 7:00北京时间 → DST→6:00, 真太阳时 ~3:48
        ("乌鲁木齐", 87.6177, 7, 0, 1986, 9, 13),  # DST最后一天 7:00北京时间 → DST→6:00
        ("乌鲁木齐", 87.6177, 7, 0, 1986, 9, 14),  # DST后 7:00北京时间 → 真太阳时 ~4:54
    ]

    print("=== 真太阳时+夏令时测试 ===")
    for name, lon, hour, min_in, year, month, day in test_cases:
        adj_h, adj_m, info = adjust_birth_hour_for_true_solar(hour, min_in, lon, year, month, day)
        solar_corr = info["solar_correction_min"]
        dst_flag = " [DST-1h]" if info["dst_minus_1h"] else ""
        print(f"{name} ({lon}°E) {year}-{month:02d}-{day:02d} {hour:02d}:{min_in:02d} 北京时间 → "
              f"{adj_h:02d}:{adj_m:02d} 真太阳时{dst_flag} (修正 {solar_corr:+d}分钟)")

    print("\n=== 夏令时边界（给定历史数据）===")
    for year, ((sm, sd), (em, ed)) in CHINA_DST_PERIODS.items():
        print(f"{year}年: DST {year}-{sm:02d}-{sd:02d} ~ {year}-{em:02d}-{ed:02d}")

    print("\n=== 城市查询测试 ===")
    for city in ["乌鲁木齐", "上海", "北京", "拉萨"]:
        try:
            coords = get_city_coordinates(city)
            print(f"{city}: {coords}")
        except ValueError as e:
            print(f"{city}: {e}")
