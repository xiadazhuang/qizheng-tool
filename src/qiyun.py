"""
八字起运（qiyun）计算模块
===========================
算法依据：
- 《渊海子平》《三命通会》等古籍
- 《四柱预测学入门》（邵伟华）
- 现代网络教程（360Doc、水墨先生、网易等）

核心公式：3天 = 1年（余数 × 4 = 月数）
方向规则：阳男阴女顺排，阴男阳女逆排
"""

import sxtwl
import swisseph as swe
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any, List
from lunar import calculate_bazi

# 天干地支
Gan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
Zhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 二十四节气名称（对应 sxtwl 的 jqIndex 0-23）
JieQiNames = [
    "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",  # 0-5
    "春分", "清明", "谷雨", "立夏", "小满", "芒种",  # 6-11
    "夏至", "小暑", "大暑", "立秋", "处暑", "白露",  # 12-17
    "秋分", "寒露", "霜降", "立冬", "小雪", "大雪",  # 18-23
]

# 十二节气（节令，用于起运计算）
JieNames = {"立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
            "立秋", "白露", "寒露", "立冬", "大雪", "小寒"}

# 六十甲子（0=甲子）
JiaZi = [(i % 10, i % 12) for i in range(60)]


def jd_to_beijing(jd: float) -> datetime:
    """
    将儒略日（JD）转换为北京时 datetime。
    
    注意：swe.revjul() 返回 UTC 时间的各分量，
    而 sxtwl 的 JD 是以北京时（UTC+8）为基准的，
    所以我们需要将 UTC 分量加上 8 小时得到北京时。
    """
    year, month, day, hour = swe.revjul(jd)
    sec = (hour % 1) * 60
    minute = int(sec)
    second = int((sec % 1) * 60)
    utc_dt = datetime(int(year), int(month), int(day),
                      int(hour), minute, second)
    return utc_dt + timedelta(hours=8)


def beijing_to_jd(dt: datetime) -> float:
    """
    将北京时 datetime 转换为儒略日（JD）。
    
    sxtwl 的 JD 使用北京时作为参考，
    swe.julday() 需要 UTC 时间，
    所以先将北京时转为 UTC（减8小时），再计算 JD。
    """
    utc_dt = dt - timedelta(hours=8)
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                      utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)


def get_year_stem(birth_year: int, birth_month: int,
                  birth_day: int) -> int:
    """获取年干索引（0=甲,...,9=癸）"""
    d = sxtwl.Day.fromSolar(birth_year, birth_month, birth_day)
    yg = d.getYearGZ()
    return yg.tg


def get_jieqi_years(birth_year: int) -> List[Dict[str, Any]]:
    """
    获取指定年份附近的所有节气（含精确时间）。
    覆盖 birth_year-1 到 birth_year+1 年，
    以确保涵盖跨越年份边界的节气（如1990年10月需用到1989年的寒露）。
    
    Returns:
        按 JD 排序的节气列表，每项含 jqIndex, name, jd, dt(北京时间)
    """
    all_jieqi = []
    for year in range(birth_year - 1, birth_year + 2):
        for elem in sxtwl.getJieQiByYear(year):
            all_jieqi.append({
                "jqIndex": elem.jqIndex,
                "name": JieQiNames[elem.jqIndex],
                "jd": elem.jd,
                "dt": jd_to_beijing(elem.jd),
            })
    all_jieqi.sort(key=lambda x: x["jd"])
    return all_jieqi


def is_yang_stem(stem_tg: int) -> bool:
    """天干阴阳：甲丙戊庚壬=阳（索引0,2,4,6,8）"""
    return stem_tg % 2 == 0


def get_direction(gender: str, year_stem_tg: int) -> int:
    """
    判断起运方向。
    
    规则：阳男阴女顺（到下一个节气），
          阴男阳女逆（到上一个节气）。
    
    Returns:
        1 = 顺行（next jieqi），-1 = 逆行（prev jieqi）
    """
    yang = is_yang_stem(year_stem_tg)
    male = gender in ["男", "M"]
    # 同阴阳则顺，不同则逆
    if (yang and male) or (not yang and not male):
        return 1
    return -1


def find_target_jieqi(birth_jd: float, direction: int,
                      all_jieqi: List[Dict]) -> Optional[Dict]:
    """
    找到起运计算对应的目标节气。
    
    Args:
        birth_jd: 出生时刻的 JD（sxtwl 北京时参考系）
        direction: 1=下一个节气，-1=上一个节气
        all_jieqi: 所有节气列表（含 JD 和 dt）
    
    Returns:
        目标节气 dict，含 gap_days（出生到节气的天数）
    """
    # 只保留十二节气
    jie_only = [j for j in all_jieqi if j["name"] in JieNames]
    
    target = None
    if direction == 1:  # 顺：下一个节气（严格在出生之后）
        for j in jie_only:
            if j["jd"] > birth_jd + 1e-9:
                target = dict(j)
                target["gap_days"] = target["jd"] - birth_jd
                break
    else:  # 逆：上一个节气（严格在出生之前）
        for j in reversed(jie_only):
            if j["jd"] < birth_jd - 1e-9:
                target = dict(j)
                target["gap_days"] = birth_jd - target["jd"]
                break
    
    return target


def days_to_age(gap_days: float) -> Tuple[int, int, float]:
    """
    将天数转换为起运岁数。
    
    传统公式：
    - 总天数 ÷ 3 = 起运年数（精确值）
    - 整数部分 = 岁数
    - 余数（天数 % 3）× 4 = 零头月数（0、4、8）
    
    Args:
        gap_days: 出生到目标节气的天数（含小数）
    
    Returns:
        (years, months, total_years_float)
    """
    total_years = gap_days / 3.0
    years = int(total_years)
    frac = total_years - years  # 0~3 范围的小数
    
    # 处理浮点误差：如果 frac 接近 3，调整到下一岁
    if frac >= 2.999:
        years += 1
        months = 0
    else:
        rem = round(frac * 3)  # 0, 1, 2
        months = rem * 4
    
    return years, months, total_years


def qiyun_to_date(birth_dt: datetime, total_years: float) -> datetime:
    """
    将起运岁数（精确值）转换为具体日期。
    
    使用 365.25 天/年 换算。
    """
    total_days = total_years * 365.25
    return birth_dt + timedelta(days=total_days)


def dayun_sequence(month_gz: str, direction: int, num: int = 8) -> List[str]:
    """
    计算大运干支序列（从月柱出发）。
    
    Args:
        month_gz: 月柱，如 "丙戌"
        direction: 1=顺行（往后数），-1=逆行（往前数）
        num: 计算几步大运
    
    Returns:
        大运干支列表，如 ["丁亥", "戊子", ...]
    """
    month_gz_tg = Gan.index(month_gz[0])
    month_gz_dz = Zhi.index(month_gz[1])
    
    # 找月柱在六十甲子中的位置
    month_idx = None
    for i, (tg, dz) in enumerate(JiaZi):
        if tg == month_gz_tg and dz == month_gz_dz:
            month_idx = i
            break
    if month_idx is None:
        raise ValueError(f"Invalid month GZ: {month_gz}")
    
    stems = []
    for step in range(1, num + 1):
        if direction == 1:
            idx = (month_idx + step) % 60
        else:
            idx = (month_idx - step) % 60
        tg, dz = JiaZi[idx]
        stems.append(Gan[tg] + Zhi[dz])
    
    return stems


def calculate_qiyun(birth_date: str, birth_time: str,
                     gender: str = "男",
                     late_zichen: bool = True) -> Dict[str, Any]:
    """
    计算完整起运信息。
    
    Args:
        birth_date: 出生日期，"YYYY-MM-DD"
        birth_time: 出生时间，"HH:MM"
        gender: "男" 或 "女"
        late_zichen: 是否使用晚子时规则
    
    Returns:
        dict，含：
        - birth_dt_str: 出生时间字符串
        - year_stem: 年干
        - year_stem_tg: 年干索引
        - is_yang: 是否阳年
        - gender: 性别
        - direction: 1=顺, -1=逆
        - direction_name: "顺行" 或 "逆行"
        - target_jieqi: 目标节气名称
        - target_jieqi_dt: 目标节气北京时间字符串
        - gap_days: 出生到节气天数
        - qiyun_years: 整数岁数
        - qiyun_months: 零头月数
        - qiyun_total_years: 精确岁数
        - qiyun_date: 起运日期字符串
        - month_gz: 月柱
        - first_dayun: 首步大运干支
        - dayun_stems: 大运序列
    """
    year, month, day = map(int, birth_date.split("-"))
    hour, minute = map(int, birth_time.split(":"))
    
    # 北京时 datetime 和 JD
    birth_dt = datetime(year, month, day, hour, minute, 0)
    birth_jd = beijing_to_jd(birth_dt)
    
    # 年干
    year_stem_tg = get_year_stem(year, month, day)
    
    # 八字（含月柱）
    bazi = calculate_bazi(year, month, day, hour, minute,
                          late_zichen=late_zichen)
    
    # 方向
    direction = get_direction(gender, year_stem_tg)
    direction_name = "顺行" if direction == 1 else "逆行"
    
    # 所有节气
    all_jieqi = get_jieqi_years(year)
    
    # 目标节气
    target = find_target_jieqi(birth_jd, direction, all_jieqi)
    if target is None:
        raise ValueError("无法找到对应节气，请检查出生日期")
    
    gap_days = target["gap_days"]
    years, months, total_years = days_to_age(gap_days)
    
    # 起运日期
    qiyun_dt = qiyun_to_date(birth_dt, total_years)
    
    # 大运序列
    dayun_stems = dayun_sequence(bazi["month"], direction)
    
    return {
        "birth_dt_str": birth_dt.strftime("%Y-%m-%d %H:%M"),
        "year_stem": Gan[year_stem_tg],
        "year_stem_tg": year_stem_tg,
        "is_yang": is_yang_stem(year_stem_tg),
        "gender": gender,
        "direction": direction,
        "direction_name": direction_name,
        "target_jieqi": target["name"],
        "target_jieqi_dt": target["dt"].strftime("%Y-%m-%d %H:%M"),
        "gap_days": round(gap_days, 4),
        "qiyun_years": years,
        "qiyun_months": months,
        "qiyun_total_years": round(total_years, 4),
        "qiyun_date": qiyun_dt.strftime("%Y-%m-%d"),
        "month_gz": bazi["month"],
        "first_dayun": dayun_stems[0] if dayun_stems else None,
        "dayun_stems": dayun_stems,
    }


def format_qiyun(result: Dict[str, Any]) -> str:
    """格式化输出起运结果"""
    lines = []
    lines.append("【起运信息】")
    lines.append(f"  出生: {result['birth_dt_str']} (北京时间)")
    lines.append(f"  性别: {result['gender']}")
    lines.append(f"  年干: {result['year_stem']} ({'阳' if result['is_yang'] else '阴'}年)")
    lines.append(f"  方向: {result['direction_name']}")
    lines.append(f"  月柱: {result['month_gz']}")
    lines.append(f"  目标节气: {result['target_jieqi']} ({result['target_jieqi_dt']})")
    lines.append(f"  距节气: {result['gap_days']:.4f} 天")
    
    if result["qiyun_months"] > 0:
        lines.append(f"  起运: {result['qiyun_years']}岁{result['qiyun_months']}个月"
                     f" (精确: {result['qiyun_total_years']:.4f}岁)")
    else:
        lines.append(f"  起运: {result['qiyun_years']}岁"
                     f" (精确: {result['qiyun_total_years']:.4f}岁)")
    
    lines.append(f"  起运日期: {result['qiyun_date']}")
    lines.append(f"  首步大运: {result['first_dayun']}")
    lines.append(f"  大运序列: {' / '.join(result['dayun_stems'])}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 55)
    
    # 测试1：女 1990-10-23 07:00（测测App验证：4.8岁）
    r1 = calculate_qiyun("1990-10-23", "07:00", gender="女")
    print("\n【女 1990-10-23 07:00】（测测：4.8岁）")
    print(format_qiyun(r1))
    print(f"  ⚠ 测测: 4.8岁 | 我们: {r1['qiyun_total_years']:.1f}岁")
    
    # 测试2：男 1990-10-23 07:00
    r2 = calculate_qiyun("1990-10-23", "07:00", gender="男")
    print("\n【男 1990-10-23 07:00】")
    print(format_qiyun(r2))
    
    # 测试3：古籍验证 男1994年正月十七寅时 → 6岁起大运
    # 来源：k366.com "某男一九九四年正月十七寅时生...起运时间：一九九六年九月十七日"
    # 1994=甲戌年(阳)，男→顺，寅月(立春开始)，下一个节气？→ 数到本月令结束=?
    # 但古籍原文说18天/3=6岁，我们来验证
    r3 = calculate_qiyun("1994-01-17", "03:00", gender="男")
    print("\n【男 1994-01-17 03:00】（古籍验证：6岁）")
    print(format_qiyun(r3))
    
    # 测试4：古籍验证 女1994-01-17 寅时 → 4岁8个月
    r4 = calculate_qiyun("1994-01-17", "03:00", gender="女")
    print("\n【女 1994-01-17 03:00】（古籍验证：4岁8个月）")
    print(format_qiyun(r4))
    
    # 测试5：1989年三月初二寅时（阴年男）→ 逆推→清明
    # 来源：k366.com "男生于1989年...逆推到清明...正好两天=8个月"
    r5 = calculate_qiyun("1989-03-02", "03:00", gender="男")
    print("\n【男 1989-03-02 03:00】（古籍验证：约8个月）")
    print(format_qiyun(r5))
