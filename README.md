# 🐱 三体系整合命盘排盘工具

八字 + 紫微斗数 + 七政四余 三体系合一排盘工具。

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
# 网页版
streamlit run src/web_app.py

# 命令行
python3 src/cli.py -n "Gigi Wu" -d "1990-10-23" -t "07:00"
```

## 依赖

- pyswisseph - 星曜计算
- skyfield - 天文计算
- sxtwl - 八字排盘
- iztro-py - 紫微斗数
- streamlit - 网页界面
