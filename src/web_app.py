"""三体系整合命盘 - Streamlit 网页版 v3"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from integrate import calculate_integrated
from src.solar_time import get_city_coordinates, adjust_birth_hour_for_true_solar, is_dst_period

st.set_page_config(page_title="三体系整合命盘", page_icon="🐱", layout="wide")

# ─── 样式 ───────────────────────────────────────
st.markdown("""
<style>
  .main-title { font-size: 2.2em; font-weight: bold; color: #4a90d9; }
  .section    { border-left: 4px solid #4a90d9; padding: 0.5em 1em; margin: 1em 0;
                background: #f8f9fa; border-radius: 8px; }
  .bazi-card  { background: #fff8e1; border-radius: 8px; padding: 1em; text-align: center; }
  .palace     { background: #e8f4f8; border-radius: 8px; padding: 0.6em; margin: 0.3em 0;
                font-size: 0.9em; }
  .star-main  { color: #1565c0; font-weight: bold; }
  .star-minor { color: #666; font-size: 0.85em; }
  .qizheng-row{display:flex; gap:0.5em; flex-wrap:wrap;}
  .qizheng-item{background:#f0f4ff; border-radius:6px; padding:0.4em 0.8em; min-width:80px;}
</style>
""", unsafe_allow_html=True)

# ─── 传统星曜别名 ─────────────────────────────────
STAR_ALIAS = {
    'sun': '太阳', 'moon': '月亮', 'venus': '太白', 'mercury': '辰星',
    'jupiter': '岁星', 'mars': '荧惑', 'saturn': '镇星'
}
PCN = {'sun':'太阳','moon':'月亮','venus':'金星','mercury':'水星',
       'jupiter':'木星','mars':'火星','saturn':'土星'}

# ─── 十二宫顺序（用于绘制命盘图）───────────────────
PALACE_ORDER = ['命宫','兄弟宫','夫妻宫','子女宫','财帛宫','疾厄宫',
                '迁移宫','交友宫','事业宫','田宅宫','福德宫','父母宫']

# ─── 十二宫星曜绘制 ────────────────────────────────
def render_12palaces(palaces):
    """把palaces列表按标准顺序排列，返回html"""
    palace_dict = {p['name']: p for p in palaces}
    rows = []
    for name in PALACE_ORDER:
        p = palace_dict.get(name, {})
        major = p.get('major_stars', []) or []
        minor = p.get('minor_stars', []) or []
        main_stars = f"<span class='star-main'>{' '.join(major)}</span>"
        sub_stars = f"<span class='star-minor'>{' '.join(minor)}</span>" if minor else ""
        content = main_stars
        if sub_stars:
            content += f"<br>{sub_stars}"
        rows.append(f"<div class='palace'><b>{name}</b><br>{content}</div>")
    return rows

# ─── 主程序 ──────────────────────────────────────
st.markdown('<p class="main-title">🐱 三体系整合命盘排盘工具</p>', unsafe_allow_html=True)

col_input, col_info = st.columns([1, 1])
with col_input:
    with st.form("chart_form"):
        name   = st.text_input("姓名", value="Gigi Wu")
        date   = st.text_input("出生日期", value="1990-10-23")
        time_v = st.text_input("出生时间（HH:MM）", value="07:00")
        city   = st.text_input("出生城市（留空则使用下方经纬度）", value="")
        lat    = st.number_input("纬度", value=31.3, step=0.1)
        lon    = st.number_input("经度", value=120.6, step=0.1)
        gender = st.selectbox("性别", ["女", "男"], index=0)
        sub    = st.form_submit_button("🚀 排盘")

if sub:
    try:
        # 解析年月日
        year, month, day = map(int, date.split('-'))

        # 处理城市名 → 经纬度
        if city.strip():
            try:
                coords = get_city_coordinates(city.strip())
                lat, lon = coords[0], coords[1]
                st.info(f"📍 城市「{city}」经纬度: ({lat:.4f}, {lon:.4f})")
            except ValueError as e:
                st.warning(f"{e}，使用手动输入的经纬度。")

        # 真太阳时修正（传入年月日以支持夏令时判断）
        hour = int(time_v.split(':')[0])
        min_v = int(time_v.split(':')[1]) if ':' in time_v else 0
        adj_h, adj_m, info = adjust_birth_hour_for_true_solar(hour, min_v, lon, year, month, day)
        time_str = f"{adj_h:02d}:{adj_m:02d}"

        # 输出修正说明
        solar_corr = info["solar_correction_min"]
        if info["dst_minus_1h"]:
            base_h = (hour - 1) if hour >= 1 else 23
            base_str = f"{base_h:02d}:{min_v:02d}"
            st.info(f"☀️ 夏令时修正: {year}年出生（夏令时期间），北京时间 {hour:02d}:{min_v:02d} - 1小时 → {base_str}")
            st.info(f"☀️ 真太阳时修正: 北京时间 {base_str} → 真太阳时 {adj_h:02d}:{adj_m:02d} (经度 {lon:.1f}°E，修正 {solar_corr:+d}分钟)")
        elif adj_h != hour or adj_m != min_v:
            st.info(f"☀️ 真太阳时修正: 北京时间 {hour:02d}:{min_v:02d} → 真太阳时 {adj_h:02d}:{adj_m:02d} (修正 {solar_corr:+d}分钟)")

        result = calculate_integrated(name, date, time_str, lat, lon, gender)
        b      = result["bazi"]
        st.success(f"✅ {name}  |  {date} {time_str}  |  {gender}")

        # ─── 基础信息 ──────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("年柱", b["year"])
        with c2: st.metric("月柱", b["month"])
        with c3: st.metric("日柱", b["day"])
        with c4: st.metric("时柱", b["hour"])

        # ─── 紫微斗数 ───────────────────────────────
        ziwei = result.get("ziwei") or {}
        if "error" not in ziwei:
            st.markdown("### 🔮 紫微斗数")
            ic1, ic2, ic3 = st.columns(3)
            with ic1: st.metric("五行局", str(ziwei.get("five_elements", "N/A")))
            with ic2: st.metric("命宫", str(ziwei.get("zodiac", "N/A")))
            with ic3: st.metric("身宫", str(ziwei.get("soul", "N/A")))

            # 十二宫网格
            st.markdown("**📋 十二宫星曜**")
            palaces = ziwei.get("palaces", [])
            palace_rows = render_12palaces(palaces)
            for i in range(0, 12, 3):
                row = palace_rows[i:i+3]
                cols = st.columns(3)
                for j, html in enumerate(row):
                    with cols[j]:
                        st.markdown(html, unsafe_allow_html=True)

        # ─── 七政四余 ───────────────────────────────
        st.markdown("### 🌟 七政四余")
        planets = result.get("qizheng", {})
        siyu    = result.get("siyu", {})

        # 七政
        st.markdown("**七政（日月金水木火土）**")
        cols7 = st.columns(7)
        for i, (k, v) in enumerate(planets.items()):
            alias = STAR_ALIAS.get(k, PCN.get(k, k))
            deg = v['degree'] if isinstance(v, dict) else v
            mansion = v.get('mansion', '') if isinstance(v, dict) else ''
            with cols7[i]:
                st.metric(alias, f"{deg:.1f}°\n{mansion}宿")

        # 四余
        st.markdown("**四余（罗睺·计都·月孛·紫炁）**")
        cols4 = st.columns(4)
        for i, (k, label) in enumerate([("luohou","罗睺"),("jitu","计都"),("yuebo","月孛"),("ziqi","紫炁")]):
            with cols4[i]:
                st.metric(label, f"{siyu.get(k, 0):.1f}°")

        # ─── 完整 JSON ─────────────────────────────
        with st.expander("📄 JSON 完整数据"):
            st.json(result)

    except Exception as e:
        st.error(f"❌ 错误: {e}")
