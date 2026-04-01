"""三体系整合命盘 - Streamlit 网页"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from integrate import calculate_integrated

st.set_page_config(page_title="三体系整合命盘", page_icon="🐱")
st.title("🐱 三体系整合命盘")

with st.form("chart_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("姓名", value="Gigi Wu")
        date = st.text_input("出生日期", value="1990-10-23")
        time_val = st.text_input("出生时间", value="07:00")
    with col2:
        lat = st.number_input("纬度", value=31.3, step=0.1)
        lon = st.number_input("经度", value=120.6, step=0.1)
        gender = st.selectbox("性别", ["女", "男"], index=0)
    submitted = st.form_submit_button("排盘")

if submitted:
    try:
        result = calculate_integrated(name, date, time_val, lat, lon, gender)
        b = result["bazi"]
        st.success("{} | {} {} | {}".format(name, date, time_val, gender))
        
        # 八字
        st.subheader("🎴 八字")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("年柱", b["year"])
        with c2: st.metric("月柱", b["month"])
        with c3: st.metric("日柱", b["day"])
        with c4: st.metric("时柱", b["hour"])
        
        # 紫微斗数
        ziwei = result.get("ziwei") or {}
        if "error" not in ziwei:
            st.subheader("🔮 紫微斗数")
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("五行局", str(ziwei.get("five_elements", "N/A")))
            with c2: st.metric("命宫", str(ziwei.get("zodiac", "N/A")))
            with c3: st.metric("身宫", str(ziwei.get("soul", "N/A")))
            
            st.markdown("**十二宫星曜**")
            cols = st.columns(3)
            palaces = ziwei.get("palaces", [])
            for i, p in enumerate(palaces):
                major = p.get("major_stars") or []
                minor = p.get("minor_stars") or []
                all_stars = major + minor
                if all_stars:
                    with cols[i % 3]:
                        st.markdown("**{}**: {}".format(
                            p.get("name", p.get("name", "")),
                            ", ".join(all_stars)))
        
        # 七政四余
        st.subheader("🌟 七政")
        planets = result.get("qizheng", {})
        PCN = {"sun":"太阳","moon":"月亮","venus":"金星","mercury":"水星",
               "jupiter":"木星","mars":"火星","saturn":"土星"}
        cols = st.columns(7)
        for i, (k, v) in enumerate(planets.items()):
            with cols[i % 7]:
                st.metric(PCN.get(k, k), "{:.1f}°".format(v))
        
        st.subheader("🌙 四余")
        siyu = result.get("siyu", {})
        sy_cols = st.columns(4)
        sy_items = [("luohou","罗睺"),("jitu","计都"),("yuebo","月孛"),("ziqi","紫炁")]
        for i, (k, label) in enumerate(sy_items):
            with sy_cols[i]:
                st.metric(label, "{:.1f}°".format(siyu.get(k, 0)))
        
        # JSON
        with st.expander("JSON完整数据"):
            st.json(result)
    except Exception as e:
        st.error("错误: {}".format(e))
