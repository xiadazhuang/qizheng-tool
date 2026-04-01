"""七政四余排盘工具 - Streamlit 网页界面"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from integrate import calculate_integrated as calculate_qizheng
import json

st.set_page_config(page_title="七政四余排盘", page_icon="🐱")
st.title("🐱 七政四余排盘工具")

with st.form("bazi_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("姓名", value="Gigi Wu")
        date = st.text_input("出生日期", value="1990-10-23")
    with col2:
        time = st.text_input("出生时间", value="07:00")
        lat = st.number_input("纬度", value=31.3, step=0.1)
        lon = st.number_input("经度", value=120.6, step=0.1)
    
    submitted = st.form_submit_button("排盘")

if submitted:
    try:
        result = calculate_qizheng(name, date, time, lat, lon)
        b = result["bazi"]
        
        st.success(f"✅ {name} | {date} {time} | 女命")
        
        # 八字
        st.subheader("📋 八字")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("年柱", b["year"])
        with col2:
            st.metric("月柱", b["month"])
        with col3:
            st.metric("日柱", b["day"])
        with col4:
            st.metric("时柱", b["hour"])
        
        # 紫微斗数
        ziwei = result.get("ziwei")
        if ziwei and "error" not in ziwei:
            st.subheader("⭐ 紫微斗数")
            cols = st.columns(3)
            with cols[0]:
                st.metric("五行局", ziwei.get("five_elements", "N/A"))
            with cols[1]:
                st.metric("命宫", ziwei.get("zodiac", "N/A"))
            with cols[2]:
                st.metric("身宫", ziwei.get("soul", "N/A"))
            
            # 十二宫
            cols = st.columns(2)
            palaces_left = ziwei.get("palaces", [])[:6]
            palaces_right = ziwei.get("palaces", [])[6:]
            with cols[0]:
                for p in palaces_left:
                    if p["major_stars"]:
                        st.write(f"**{p['name']}**: {','.join(p['major_stars'])}")
            with cols[1]:
                for p in palaces_right:
                    if p["major_stars"]:
                        st.write(f"**{p['name']}**: {','.join(p['major_stars'])}")
        
        # 七政
        st.subheader("🌟 七政四余")
        cols = st.columns(7)
        planets = result["qizheng"]
        names = ["sun","moon","venus","mercury","jupiter","mars","saturn"]
        labels = ["太阳","月亮","金星","水星","木星","火星","土星"]
        for i, (k, l) in enumerate(zip(names, labels)):
            if k in planets:
                with cols[i]:
                    st.metric(l, f"{planets[k]:.1f}°")
        
        # 四余
        siyu = result["siyu"]
        cols = st.columns(4)
        for i, (k, l) in enumerate(zip(["luohou","jitu","yuebo","ziqi"], ["罗睺","计都","月孛","紫炁"])):
            if k in siyu:
                with cols[i]:
                    st.metric(l, f"{siyu[k]:.1f}°")
        
        # JSON详情
        with st.expander("JSON完整数据"):
            st.json(result)
    except Exception as e:
        st.error(f"错误: {e}")