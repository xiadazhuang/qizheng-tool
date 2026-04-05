#!/usr/bin/env python3
"""三体系整合命盘 CLI - 八字 + 紫微斗数 + 七政四余"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.integrate import calculate_integrated, to_text
from src.solar_time import get_city_coordinates, adjust_birth_hour_for_true_solar

def main():
    p = argparse.ArgumentParser(description='三体系整合命盘排盘工具')
    p.add_argument('-n', '--name', required=True, help='姓名')
    p.add_argument('-d', '--date', required=True, help='阳历出生日期 YYYY-MM-DD')
    p.add_argument('-t', '--time', required=True, help='出生时间 HH:MM')
    p.add_argument('--lat', type=float, default=31.3, help='纬度（默认31.3）')
    p.add_argument('--lon', type=float, default=None, help='出生地经度（默认120.6，需配合 --city 使用）')
    p.add_argument('-c', '--city', type=str, default=None,
                   help='出生城市名（如"乌鲁木齐"），自动查经度并计算真太阳时')
    p.add_argument('-g', '--gender', default='女', choices=['女','男'], help='性别')
    p.add_argument('-j', '--json', action='store_true', help='输出JSON格式')
    p.add_argument('--no-solar-time', action='store_true',
                   help='禁用真太阳时修正，使用原始北京时间计算八字')
    args = p.parse_args()

    # 处理出生时间和经度
    birth_hour = int(args.time.split(':')[0])
    birth_min = int(args.time.split(':')[1]) if ':' in args.time and len(args.time.split(':')) > 1 else 0

    lat = args.lat
    lon = args.lon

    # 如果指定了城市名，查经度
    if args.city:
        coords = get_city_coordinates(args.city)
        lat, lon = coords[0], coords[1]
        print(f"📍 城市「{args.city}」经纬度: ({lat:.4f}, {lon:.4f})")

    # 默认经度
    if lon is None:
        lon = 120.6

    # 真太阳时修正（默认启用）
    true_solar_hour = birth_hour
    true_solar_min = birth_min
    if not args.no_solar_time:
        true_solar_hour, true_solar_min = adjust_birth_hour_for_true_solar(birth_hour, birth_min, lon)
        if true_solar_hour != birth_hour or true_solar_min != birth_min:
            print(f"☀️ 真太阳时修正: 北京时间 {birth_hour:02d}:{birth_min:02d} → 真太阳时 {true_solar_hour:02d}:{true_solar_min:02d} "
                  f"(经度 {lon:.1f}°E，修正 {(lon-120)*4:+.0f}分钟)")

    time_str = f"{true_solar_hour:02d}:{true_solar_min:02d}"

    result = calculate_integrated(args.name, args.date, time_str,
                                  lat, lon, args.gender)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(to_text(result))

if __name__ == '__main__':
    main()
