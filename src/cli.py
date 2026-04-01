#!/usr/bin/env python3
"""七政四余排盘工具 CLI"""
import argparse
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core import calculate_qizheng

def main():
    parser = argparse.ArgumentParser(description='七政四余排盘工具')
    parser.add_argument('--name', '-n', required=True, help='姓名')
    parser.add_argument('--date', '-d', required=True, help='阳历出生日期 YYYY-MM-DD')
    parser.add_argument('--time', '-t', required=True, help='出生时间 HH:MM')
    parser.add_argument('--lat', default='31.3', help='纬度（默认苏州31.3）')
    parser.add_argument('--lon', default='120.6', help='经度（默认苏州120.6）')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    args = parser.parse_args()

    result = calculate_qizheng(args.name, args.date, args.time,
                              float(args.lat), float(args.lon))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        b = result['bazi']
        print(f"八  字：{b['year']} / {b['month']} / {b['day']} / {b['hour']}")
        print(f"出生：{result['birth']['date']} {result['birth']['time']}")
        print(f"七政：")
        for k, v in result['qizheng'].items():
            print(f"  {k}: {v['degree']:.2f}° → {v['mansion']}宿")
        print(f"四余：")
        for k, v in result['siyu'].items():
            print(f"  {k}: {v:.2f}°")

if __name__ == '__main__':
    main()
