"""八字计算 - 基于 sxtwl 库"""
import sxtwl

Gan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
Zhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]


def calculate_bazi(year, month, day, hour, minute=0, late_zichen=True):
    """
    计算完整八字

    Args:
        late_zichen: 是否使用晚子时规则
            - True:  23:00-23:59 → 日柱属下一天，时柱=子时
            - False: sxtwl默认规则（23:00-23:59 → 当天，子时）
    """
    from zs_remnants import adjust_zichen_boundary

    if late_zichen:
        day_str = f"{year:04d}-{month:02d}-{day:02d}"
        adj_date, adj_hour, adj_min, needs_override, override_gan_zhi = \
            adjust_zichen_boundary(day_str, hour, minute)

        adj_y, adj_m, adj_d = map(int, adj_date.split('-'))
        result = sxtwl.fromSolar(adj_y, adj_m, adj_d)

        yg = result.getYearGZ()
        mg = result.getMonthGZ()
        dg = result.getDayGZ()

        if needs_override:
            # 23:00-23:59 → 子时（override）
            hour_gan_zhi = override_gan_zhi
        else:
            hg = result.getHourGZ(adj_hour)
            hour_gan_zhi = Gan[hg.tg] + Zhi[hg.dz]

        return {
            "year":  Gan[yg.tg] + Zhi[yg.dz],
            "month": Gan[mg.tg] + Zhi[mg.dz],
            "day":   Gan[dg.tg] + Zhi[dg.dz],
            "hour":  hour_gan_zhi,
        }
    else:
        result = sxtwl.fromSolar(year, month, day)
        yg = result.getYearGZ()
        mg = result.getMonthGZ()
        dg = result.getDayGZ()
        hg = result.getHourGZ(hour)
        return {
            "year":  Gan[yg.tg] + Zhi[yg.dz],
            "month": Gan[mg.tg] + Zhi[mg.dz],
            "day":   Gan[dg.tg] + Zhi[dg.dz],
            "hour":  Gan[hg.tg] + Zhi[hg.dz],
        }


def solar_to_lunar(year, month, day):
    """阳历转农历"""
    result = sxtwl.fromSolar(year, month, day)
    return {
        "year": result.getLunarYear(),
        "month": result.getLunarMonth(),
        "day": result.getLunarDay(),
    }


if __name__ == "__main__":
    # 测试晚子时规则
    print("=== 晚子时规则（默认）===")
    # 1990-10-23 23:30 → 晚子时：日期+1天=10-24，子时
    bazi_late = calculate_bazi(1990, 10, 23, 23, 30, late_zichen=True)
    print(f"1990-10-23 23:30 (晚子时): {bazi_late['year']} / {bazi_late['month']} / {bazi_late['day']} / {bazi_late['hour']}")

    # 1990-10-23 00:30 → 丑时（不变）
    bazi_late2 = calculate_bazi(1990, 10, 23, 0, 30, late_zichen=True)
    print(f"1990-10-23 00:30 (晚子时): {bazi_late2['year']} / {bazi_late2['month']} / {bazi_late2['day']} / {bazi_late2['hour']}")

    print("\n=== 标准规则（sxtwl默认）===")
    bazi_std = calculate_bazi(1990, 10, 23, 23, 30, late_zichen=False)
    print(f"1990-10-23 23:30 (标准):   {bazi_std['year']} / {bazi_std['month']} / {bazi_std['day']} / {bazi_std['hour']}")
