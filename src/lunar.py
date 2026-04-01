"""八字计算 - 基于 sxtwl 库"""
import sxtwl

Gan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
Zhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

lunar = sxtwl.Lunar()

def calculate_bazi(year, month, day, hour, minute=0):
    """计算完整八字"""
    result = lunar.getDayBySolar(year, month, day)
    
    # 年柱
    year_gan = Gan[result.Lyear2.tg]
    year_zhi = Zhi[result.Lyear2.dz]
    
    # 月柱
    month_gan = Gan[result.Lmonth2.tg]
    month_zhi = Zhi[result.Lmonth2.dz]
    
    # 日柱
    day_gan = Gan[result.Lday2.tg]
    day_zhi = Zhi[result.Lday2.dz]
    
    # 时柱
    time_gan_zhi = lunar.getShiGz(result.Lday2.tg, hour)
    time_gan = Gan[time_gan_zhi.tg]
    time_zhi = Zhi[time_gan_zhi.dz]
    
    return {
        "year": year_gan + year_zhi,
        "month": month_gan + month_zhi,
        "day": day_gan + day_zhi,
        "hour": time_gan + time_zhi,
    }

def solar_to_lunar(year, month, day):
    """阳历转农历"""
    result = lunar.getDayBySolar(year, month, day)
    return {"year": result.Lyear, "month": result.Lmonth, "day": result.Lday}

if __name__ == "__main__":
    bazi = calculate_bazi(1990, 10, 23, 7)
    print(f"Gigi Wu 八字: {bazi['year']} / {bazi['month']} / {bazi['day']} / {bazi['hour']}")
