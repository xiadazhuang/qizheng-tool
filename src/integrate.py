"""
三体系整合排盘：八字 + 紫微斗数 + 七政四余
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import swisseph as swe
from seven_planets import calculate_seven_planets
from mansions import map_to_mansion
from four_remnants import calculate_luohou, calculate_jitu, calculate_yuebo, calculate_ziqi
from lunar import calculate_bazi, solar_to_lunar

try:
    from iztro_py import by_solar as _ziwei_by_solar
    _HAS_ZIWAR = True
except ImportError:
    _HAS_ZIWAR = False

STAR_MAP = {
    'tianzhu': '紫微', 'tianji': '天机', 'taiyang': '太阳', 'wuqu': '武曲',
    'tiantong': '天同', 'lianzhen': '廉贞', 'pojun': '破军', 'tanlang': '贪狼',
    'jumen': '巨门', 'luocun': '禄存', 'tianliang': '天梁', 'qisha': '七杀',
    'wenqu': '文曲', 'zuofu': '左辅', 'youbi': '右弼', 'tiankui': '天魁', 'tianyue': '天钺',
    'tianfu': '天府', 'tianyin': '太阴', 'taiyin': '太阴', 'tianxiang': '天相', 'qingyang': '擎羊', 'ziwei': '紫微',
    'huoxing': '火星', 'lingxing': '铃星', 'tianma': '天马',
}

PALACE_MAP = {
    'siblingsPalace': '兄弟宫', 'soulPalace': '身宫', 'parentsPalace': '父母宫',
    'propertyPalace': '田宅宫', 'careerPalace': '官禄宫', 'friendsPalace': '交友宫',
    'surfacePalace': '迁移宫', 'healthPalace': '疾厄宫', 'wealthPalace': '财帛宫',
    'childrenPalace': '子女宫', 'spousePalace': '夫妻宫',
    'spiritPalace': '福德宫',
}


def _cn_star(name):
    n = name.lower()
    for k, v in STAR_MAP.items():
        if k in n:
            return v
    # 去掉Maj/Min/Adj后缀
    base = re.sub(r'(maj|min|adj)$', '', n, flags=re.I)
    for k, v in STAR_MAP.items():
        if k in base:
            return v
    return name


def _cn_palace(name):
    n = name.lower()
    for k, v in PALACE_MAP.items():
        if k.lower() in n:
            return v
    return name


def _format_palace(palace):
    major = [_cn_star(s.name) for s in (palace.major_stars or [])]
    minor = [_cn_star(s.name) for s in (palace.minor_stars or [])]
    adj = [_cn_star(s.name) for s in (palace.adjective_stars or [])]
    return {
        'name': _cn_palace(palace.name),
        'major_stars': major,
        'minor_stars': minor,
        'adjective_stars': adj,
    }


def calculate_integrated(name, birth_date, birth_time, lat, lon, gender='女'):
    """整合八字 + 紫微斗数 + 七政四余"""
    year, month, day = map(int, birth_date.split('-'))
    hour, minute = map(int, birth_time.split(':'))
    jd = swe.julday(year, month, day, hour + minute/60.0)

    bazi = calculate_bazi(year, month, day, hour, minute)
    lunar = solar_to_lunar(year, month, day)
    raw_planets = calculate_seven_planets(jd)
    # 加入二十八宿名称
    planets = {}
    for k, deg in raw_planets.items():
        mansion, inner = map_to_mansion(deg)
        planets[k] = {'degree': deg, 'mansion': mansion, 'inner': round(inner, 2)}
    siyu = {
        'luohou': calculate_luohou(jd),
        'jitu': calculate_jitu(jd),
        'yuebo': calculate_yuebo(jd),
        'ziqi': calculate_ziqi(jd),
    }

    ziwei = None
    if _HAS_ZIWAR:
        try:
            chart = _ziwei_by_solar(f'{year}-{month:02d}-{day:02d}', hour, gender)
            ziwei = {
                'five_elements': str(chart.five_elements_class),
                'zodiac': str(chart.zodiac),
                'soul': str(chart.soul),
                'palaces': [_format_palace(p) for p in chart.palaces],
            }
        except Exception as e:
            ziwei = {'error': str(e)}

    return {
        'name': name,
        'birth': {'date': birth_date, 'time': birth_time, 'lat': lat, 'lon': lon, 'gender': gender},
        'bazi': bazi,
        'lunar': lunar,
        'qizheng': planets,
        'siyu': siyu,
        'ziwei': ziwei,
    }


def to_text(data):
    """生成可读文本"""
    lines = []
    lines.append("=" * 50)
    lines.append(f"三体系整合命盘 - {data['name']}")
    lines.append("=" * 50)

    b = data['bazi']
    lines.append(f"\n【八字】{b['year']} / {b['month']} / {b['day']} / {b['hour']}")

    lunar = data.get('lunar', {})
    lines.append(f"农历: {lunar.get('year','')}年{lunar.get('month','')}月{lunar.get('day','')}日")

    ziwei = data.get('ziwei')
    if ziwei and 'error' not in ziwei:
        lines.append(f"\n【紫微斗数】")
        lines.append(f"  五行局: {ziwei.get('five_elements', 'N/A')}")
        lines.append(f"  命宫: {ziwei.get('zodiac', 'N/A')}")
        for p in ziwei.get('palaces', []):
            if p['major_stars']:
                lines.append(f"  {p['name']}: {','.join(p['major_stars'])}")

    PCN = {'sun':'太阳','moon':'月亮','venus':'金星','mercury':'水星','jupiter':'木星','mars':'火星','saturn':'土星'}
    lines.append(f"\n【七政四余】")
    for k, v in data['qizheng'].items():
        deg = v['degree'] if isinstance(v, dict) else v
        mansion = v.get('mansion', '') if isinstance(v, dict) else ''
        lines.append(f"  {PCN.get(k, k)}: {deg:.2f}° ({mansion}宿)")
    sy = data['siyu']
    lines.append(f"  罗睺: {sy['luohou']:.2f} deg")
    lines.append(f"  计都: {sy['jitu']:.2f} deg")
    lines.append(f"  月孛: {sy['yuebo']:.2f} deg")
    lines.append(f"  紫炁: {sy['ziqi']:.2f} deg")

    return '\n'.join(lines)


if __name__ == '__main__':
    result = calculate_integrated('Gigi Wu', '1990-10-23', '07:00', 31.3, 120.6, '女')
    print(to_text(result))
