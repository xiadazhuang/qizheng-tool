"""三体系整合命盘 - Streamlit 网页版 v2"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from integrate import calculate_integrated

st.set_page_config(page_title="三体系整合命盘", page_icon="🐱")
st.title("🐱 三体系整合命盘 v2")

# 传统星曜名称对照
STAR_ALIAS = {
    'sun': '太阳(岁)', 'moon': '月亮(月)', 
    'venus': '太白(金)', 'mercury': '辰星(水)',
    'jupiter': '岁星(木)', 'mars': '荧惑(火)', 'saturn': '镇星(土)'
}
SIYU_NAMES = {'luohou': '罗睺', 'jitu': '计都', 'yuebo': '月孛', 'ziqi': '紫炁'}
PCN = {'sun':'太阳','moon':'月亮','venus':'金星','mercury':'水星',
       'jupiter':'木星','mars':'火星','saturn':'土星'}

with st.form("chart_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("姓名", value="Gigi Wu")
        date = st.text_input("出生日期（YYYY-MM-DD）", value="1990-10-23")
        time_val = st.text_input("出生时间（HH:MM）", value="07:00")
    with col2:
        lat = st.number_input("出生纬度", value=31.3, step=0.1)
        lon = st.number_input("出生经度", value=120.6, step=0.1)
        gender = st.selectbox("性别", ["女", "男"], index=0)
    submitted = st.form_submit_button("🚀 排盘")

if submitted:
    try:
        result = calculate_integrated(name, date, time_val, lat, lon, gender)
        b = result["bazi"]
        st.success(f"✅ {name} | {date} {time_val} | {gender}")
        
        # === 八字 ===
        st.subheader("🎴 八字")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("年柱", b["year"])
        with c2: st.metric("月柱", b["month"])
        with c3: st.metric("日柱", b["day"])
        with c4: st.metric("时柱", b["hour"])
        
        # === 紫微斗数 ===
        ziwei = result.get("ziwei") or {}
        if "error" not in ziwei:
            st.subheader("🔮 紫微斗数")
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("五行局", str(ziwei.get("five_elements", "N/A")))
            with c2: st.metric("命宫", str(ziwei.get("zodiac", "N/A")))
            with c3: st.metric("身宫", str(ziwei.get("soul", "N/A")))
            
            # 十二宫展示
            palaces = ziwei.get("palaces", [])
            st.markdown("**📋 十二宫星曜**")
            palace_data = []
            for p in palaces:
                major = p.get("major_stars") or []
                minor = p.get("minor_stars") or []
                all_s = major + minor
                palace_data.append((p.get("name",""), ",".join(all_s) if all_s else "空宫"))
            
            # 每行3个宫
            for i in range(0, len(palace_data), 3):
                row = palace_data[i:i+3]
                cols = st.columns(3)
                for j, (宫名, 星曜) in enumerate(row):
                    with cols[j]:
                        st.markdown(f"**{宫名}**：{星曜}")
        
        # === 七政 ===
        st.subheader("🌟 七政四余（传统别名）")
        planets = result.get("qizheng", {})
        siyu = result.get("siyu", {})
        
        # 七政：同时显示传统名
        st.markdown("**七政（日月金水木火土）**")
        row1 = st.columns(7)
        for i, (k, v) in enumerate(planets.items()):
            alias = STAR_ALIAS.get(k, PCN.get(k, k))
            with row1[i]:
                st.metric(alias, f"{v:.1f}°")
        
        # 四余
        st.markdown("**四余（罗睺/计都/月孛/紫炁）**")
        row2 = st.columns(4)
        for i, (k, label) in enumerate([("luohou","罗睺"),("jitu","计都"),("yuebo","月孛"),("ziqi","紫炁")]):
            with row2[i]:
                st.metric(label, f"{siyu.get(k, 0):.1f}°")
        
        # === JSON ===
        with st.expander("📄 JSON 完整数据"):
            st.json(result)
            
    except Exception as e:
        st.error(f"❌ 错误: {e}")
