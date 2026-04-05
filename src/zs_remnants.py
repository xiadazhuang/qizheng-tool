"""
晚子时（早子时）分界规则适配器

规则：
  - 23:00-23:59 → 属下一天的子时（日柱+1天，时柱=子时）
  - 00:00-00:59 → 属当天的丑时（sxtwl已正确，无需调整）

sxtwl 默认 midnight 规则：23:00-23:59 → 属当天的子时
我们覆盖为：晚子时规则

实现方式：
  23:00-23:59 → 把日期往后推1天，小时置0，再调 sxtwl
  00:00-00:59 → 直接调 sxtwl（已是丑时，无需调整）
"""
from datetime import date, timedelta


def add_one_day(date_str):
    """把 YYYY-MM-DD 往后推1天，返回新日期字符串"""
    y, m, d = map(int, date_str.split('-'))
    new_date = date(y, m, d) + timedelta(days=1)
    return new_date.strftime('%Y-%m-%d')


def adjust_zichen_boundary(birth_date_str, birth_hour, birth_min):
    """
    晚子时规则边界修正

    Args:
        birth_date_str: 原始出生日期 YYYY-MM-DD
        birth_hour: 小时 (0-23)
        birth_min: 分钟 (0-59)

    Returns:
        (adjusted_date_str, adjusted_hour, adjusted_min, needs_hour_override, override_hour_gan_zhi)
        - needs_hour_override=False → 用 sxtwl 原生结果
        - needs_hour_override=True  → 用 override_hour_gan_zhi 替换时柱
    """
    if 23 <= birth_hour <= 23:
        # 晚子时：日期+1天，小时归0，用sxtwl算出下一天的子时
        adjusted_date = add_one_day(birth_date_str)
        return adjusted_date, 0, birth_min, False, "子时"
    else:
        # 其他时间：直接用sxtwl
        return birth_date_str, birth_hour, birth_min, False, None


def describe_zichen_rule(late_zichen: bool) -> str:
    """返回当前使用的时辰分界规则描述"""
    if late_zichen:
        return "晚子时规则（23:00后属下一天）"
    else:
        return "标准规则（23:00后属当天）"
