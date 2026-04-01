"""八字计算 - 基于 sxtwl 库"""
import sxtwl

Gan = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
Zhi = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

def calculate_bazi(year, month, day, hour, minute=0):
    """计算完整八字"""
    result = sxtwl.fromSolar(year, month, day)
    yg = result.getYearGZ()
    mg = result.getMonthGZ()
    dg = result.getDayGZ()
    hg = result.getHourGZ(hour)
    return {
        "year": Gan[yg.tg] + Zhi[yg.dz],
        "month": Gan[mg.tg] + Zhi[mg.dz],
        "day": Gan[dg.tg] + Zhi[dg.dz],
        "hour": Gan[hg.tg] + Zhi[hg.dz],
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
    bazi = calculate_bazi(1990, 10, 23, 7)
    print(f"Gigi Wu 八字: {bazi['year']} / {bazi['month']} / {bazi['day']} / {bazi['hour']}")
