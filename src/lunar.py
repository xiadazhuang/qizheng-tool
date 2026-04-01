"""
八字计算 - 基于儒略日
"""
import swisseph as swe
from lunarcalendar import Converter, Solar
from datetime import datetime
import ephem

HEAVENLY = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
EARTHLY = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 六十甲子表（索引0-59）
JIAZI = [
    '甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉',
    '甲戌', '乙亥', '丙子', '丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午', '癸未',
    '甲申', '乙酉', '丙戌', '丁亥', '戊子', '己丑', '庚寅', '辛卯', '壬辰', '癸巳',
    '甲午', '乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子', '辛丑', '壬寅', '癸卯',
    '甲辰', '乙巳', '丙午', '丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子', '癸丑',
    '甲寅', '乙卯', '丙辰', '丁巳', '戊午', '己未', '庚申', '辛酉', '壬戌', '癸亥'
]

# 月干支节气基准
MONTH_STEM_OFFSET = {
    '寅月': 0, '卯月': 1, '辰月': 2, '巳月': 3, '午月': 4, '未月': 5,
    '申月': 6, '酉月': 7, '戌月': 8, '亥月': 9, '子月': 10, '丑月': 11
}


def solar_to_lunar(year: int, month: int, day: int) -> dict:
    """
    阳历转农历
    
    Args:
        year, month, day: 阳历日期
    
    Returns:
        dict: {农历年, 农历月, 农历日, 是否闰月}
    """
    solar = Solar(year, month, day)
    lunar = Converter.Solar2Lunar(solar)
    
    return {
        "year": lunar.year,
        "month": lunar.month,
        "day": lunar.day,
        "isleap": lunar.isleap,
    }


def get_jieqi(year: int, month: int, day: int) -> str:
    """
    获取指定日期的节气
    
    Args:
        year, month, day: 阳历日期
    
    Returns:
        str: 节气名（如"寒露"）或空字符串
    """
    # pyswisseph 可以计算节气
    jd = swe.julday(year, month, day, 12)  # 中午12:00
    flags = swe.CALC_SUNTRANS | swe.TRAN_NS
    # 简化版，需要进一步完善
    return ""


def jd_to_ganzhi(jd: float) -> str:
    """
    将儒略日转换为干支（60甲子）
    
    Args:
        jd: 儒略日数
    
    Returns:
        str: 干支（如"甲子"）
    """
    # 方法: 天干=(JD-1)%10, 地支=(JD+1)%12
    # 验证: 1992-02-18 JD=2448671 -> 甲子 ✓
    #       1990-10-23 JD=2448188 -> 辛酉 ✓
    tian_gan = int(jd - 1) % 10
    di_zhi = int(jd + 1) % 12
    return HEAVENLY[tian_gan] + EARTHLY[di_zhi]


def get_julian_day(year: int, month: int, day: int, hour: int = 12, 
                   minute: int = 0, second: int = 0) -> float:
    """
    获取儒略日数（使用 ephem 库，更准确）
    
    Args:
        year, month, day, hour, minute, second: 阳历日期时间
    
    Returns:
        float: 儒略日数
    """
    # ephem.Date 返回的是儒略日 - 2415020.5
    # 所以实际JD = float(ephem.Date) + 2415020.5
    date_str = f"{year}/{month}/{day}"
    jd = float(ephem.Date(date_str)) + 2415020.5
    
    # 加上时间部分（每天 fraction）
    fraction = (hour - 12) / 24.0 + minute / 1440.0 + second / 86400.0
    return jd + fraction


def get_julian_day_swe(year: int, month: int, day: int, hour: int = 12, 
                       minute: int = 0, second: int = 0) -> float:
    """
    获取儒略日数（使用 swisseph 库）
    
    Args:
        year, month, day, hour, minute, second: 阳历日期时间
    
    Returns:
        float: 儒略日数
    """
    # swisseph 的 julday 函数
    # 注意：月份和日期需要正确传入
    jd = swe.julday(year, month, day, hour + minute/60.0 + second/3600.0)
    return jd


def calculate_year_zhu(year: int, month: int, day: int) -> str:
    """
    计算年柱（根据立春切换）
    
    年柱以立春为分界，立春前属于上一年，立春后属于当年
    
    Args:
        year, month, day: 出生日期
    
    Returns:
        str: 年干支
    """
    # 使用 swisseph 计算立春日期
    # 立春通常在2月3-5日之间
    
    # 先尝试计算当年立春
    # 用简化方法：如果日期在2月4日之前，认为还是上年
    if month < 2 or (month == 2 and day < 4):
        # 属于上一年
        adjusted_year = year - 1
    else:
        adjusted_year = year
    
    # 计算儒略日
    jd = swe.julday(adjusted_year, 1, 1, 12)
    
    # 年柱公式: (JD + 6.5) % 60
    base = int(jd + 6.5) % 60
    
    return HEAVENLY[base % 10] + EARTHLY[base % 12]


def calculate_month_zhu(year: int, month: int, day: int) -> str:
    """
    计算月柱（根据节气切换）
    
    月柱以"节"为分界，如立春是寅月的开始
    
    Args:
        year, month, day: 出生日期
    
    Returns:
        str: 月干支
    """
    # 简化版：使用近似公式
    # 月干 = (年干 * 2 + 月份) % 10
    # 其中年份需要调整（立春后新的一年）
    
    # 先计算年干（简化：使用1月1日的年干）
    jd = swe.julday(year, 1, 1, 12)
    year_gan = int(jd + 6.5) % 60 % 10
    
    # 如果是1月或2月，用上一年
    if month < 3:
        year_gan = (year_gan - 1) % 10
    
    # 月干公式: (年干 * 2 + 月份) % 10
    # 但正月是寅月，对应地支1
    month_gan = (year_gan * 2 + month) % 10
    
    # 地支：正月=寅(1), 二月=卯(2), ..., 十二月=丑(11)
    # 但需要考虑节气，这里简化处理
    month_zhi = month + 1  # 简化
    if month_zhi > 12:
        month_zhi = month_zhi - 12
    
    return HEAVENLY[month_gan] + EARTHLY[month_zhi]


def calculate_day_zhu(year: int, month: int, day: int) -> str:
    """
    计算日柱
    
    Args:
        year, month, day: 出生日期
    
    Returns:
        str: 日干支
    """
    # 使用 ephem 计算准确的儒略日
    jd = get_julian_day(year, month, day)
    return jd_to_ganzhi(jd)


def calculate_hour_zhu(day_gan: str, hour: int, minute: int) -> str:
    """
    计算时柱
    
    Args:
        day_gan: 日干（天干）
        hour: 小时 (0-23)
        minute: 分钟
    
    Returns:
        str: 时干支
    
    Note:
        时柱的地支：23-1点=子时（分晨子和夜子）
        时柱的天干公式：日干 * 2 + 时支
    """
    # 时支计算
    # 子时(23:00-01:00) = 0点开始每小时一个时辰
    # 每个时辰2小时
    if hour == 23:
        hour_zhi = 0  # 子时（夜子）
    elif hour == 0:
        hour_zhi = 0  # 子时（晨子）
    else:
        hour_zhi = (hour + 1) // 2
    
    # 时干计算：日干 * 2 + 时支
    day_gan_idx = HEAVENLY.index(day_gan)
    hour_gan = (day_gan_idx * 2 + hour_zhi) % 10
    
    return HEAVENLY[hour_gan] + EARTHLY[hour_zhi]


def calculate_bazi(year: int, month: int, day: int, hour: int, 
                   minute: int = 0, longitude: float = 120.0) -> dict:
    """
    计算八字
    
    Args:
        year, month, day, hour, minute: 出生时间
        longitude: 出生地经度（用于真太阳时校正，默认120°东八区）
    
    Returns:
        dict: {年柱, 月柱, 日柱, 时柱}
    """
    # 真太阳时校正（简化版）
    # 真太阳时 = 平太阳时 + (当地经度 - 标准经度) * 4分钟
    # 东八区标准经度120°，北京地区约116°，上海约121°
    # 这里简化不做校正
    
    # 计算各柱
    year_zhu = calculate_year_zhu(year, month, day)
    month_zhu = calculate_month_zhu(year, month, day)
    day_zhu = calculate_day_zhu(year, month, day)
    hour_zhu = calculate_hour_zhu(day_zhu[0], hour, minute)
    
    return {
        "year": year_zhu,
        "month": month_zhu,
        "day": day_zhu,
        "hour": hour_zhu,
    }


# 测试代码
if __name__ == "__main__":
    # 测试 Gigi Wu (1990-10-23 07:00)
    print("=== 测试 Gigi Wu 八字 ===")
    bazi = calculate_bazi(1990, 10, 23, 7, 0)
    print(f"出生: 1990年10月23日 07:00")
    print(f"八字: {bazi['year']} {bazi['month']} {bazi['day']} {bazi['hour']}")
    print(f"年柱: {bazi['year']}")
    print(f"月柱: {bazi['month']}")
    print(f"日柱: {bazi['day']}")
    print(f"时柱: {bazi['hour']}")
    
    print("\n=== 验证日柱 ===")
    # 验证1992-02-18应为甲子日
    day = calculate_day_zhu(1992, 2, 18)
    print(f"1992-02-18: {day} (应为甲子)")
    
    # 验证1990-10-23
    day = calculate_day_zhu(1990, 10, 23)
    print(f"1990-10-23: {day}")
