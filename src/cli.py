#!/usr/bin/env python3
"""三体系整合命盘 CLI - 八字 + 紫微斗数 + 七政四余"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.integrate import calculate_integrated, to_text

def main():
    p = argparse.ArgumentParser(description='三体系整合命盘排盘工具')
    p.add_argument('-n', '--name', required=True, help='姓名')
    p.add_argument('-d', '--date', required=True, help='阳历出生日期 YYYY-MM-DD')
    p.add_argument('-t', '--time', required=True, help='出生时间 HH:MM')
    p.add_argument('--lat', type=float, default=31.3, help='纬度（默认31.3）')
    p.add_argument('--lon', type=float, default=120.6, help='经度（默认120.6）')
    p.add_argument('-g', '--gender', default='女', choices=['女','男'], help='性别')
    p.add_argument('-j', '--json', action='store_true', help='输出JSON格式')
    args = p.parse_args()

    result = calculate_integrated(args.name, args.date, args.time,
                                  args.lat, args.lon, args.gender)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(to_text(result))

if __name__ == '__main__':
    main()
