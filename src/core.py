"""七政四余核心计算入口"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import swisseph as swe
from seven_planets import calculate_seven_planets
from four_remnants import calculate_luohou, calculate_jitu, calculate_yuebo, calculate_ziqi
from mansions import map_to_mansion
from lunar import calculate_bazi, solar_to_lunar

def calculate_qizheng(name, birth_date, birth_time, lat, lon):
    """计算完整七政四余命盘"""
    year, month, day = map(int, birth_date.split('-'))
    hour, minute = map(int, birth_time.split(':'))
    jd = swe.julday(year, month, day, hour + minute/60.0)

    # 八字
    bazi = calculate_bazi(year, month, day, hour, minute)

    # 七政
    planets = calculate_seven_planets(jd)

    # 四余
    siyu = {
        "luohou": calculate_luohou(jd),
        "jitu": calculate_jitu(jd),
        "yuebo": calculate_yuebo(jd),
        "ziqi": calculate_ziqi(jd),
    }

    # 二十八宿
    mansion_map = {}
    for planet, degree in planets.items():
        mansion, inner = map_to_mansion(degree)
        mansion_map[planet] = {"degree": degree, "mansion": mansion}

    return {
        "name": name,
        "birth": {"date": birth_date, "time": birth_time, "lat": lat, "lon": lon},
        "bazi": bazi,
        "qizheng": {k: {"degree": v, "mansion": mansion_map[k]["mansion"]} for k, v in planets.items()},
        "siyu": siyu,
        "mansions": mansion_map,
    }

if __name__ == "__main__":
    result = calculate_qizheng("Gigi Wu", "1990-10-23", "07:00", 31.3, 120.6)
    print("八字:", result["bazi"]["year"], result["bazi"]["month"], result["bazi"]["day"], result["bazi"]["hour"])
    print("应为: 庚午 / 丙戌 / 辛酉 / 壬辰")
