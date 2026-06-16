# 中职教学智能辅助系统  streamlit run Home.py
import streamlit as st

st.set_page_config(
    page_title="教学智能助手",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<h1 style="text-align:center; color:#2c5282; margin-top:60px; margin-bottom:50px; font-size:32px;">民族地区中职数学“文化-技术”融合教学案例</h1>
""", unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns(2)
with col1:
    # 纯视觉橙色按钮，不可点击，仅展示
    st.markdown('''
    <div style="width:80%;background:#ff4b4b;color:white;border:none;padding:20px;border-radius:4px;font-size:40px;text-align:center;">教师入口</div>
    ''', unsafe_allow_html=True)
    # 官方原生跳转，100%稳定不会空白
    st.page_link("pages/00_教师入口首页.py", label="点击进入教师功能", use_container_width=True)

with col2:
    st.markdown('''
    <div style="width:80%;background:#2da44e;color:white;border:none;padding:20px;border-radius:4px;font-size:40px;text-align:center;">学生入口</div>
    ''', unsafe_allow_html=True)

# 底部留白
st.markdown("<br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
# 底部备注
st.markdown("""
<div style="text-align:center; font-size:15px; color:#666; border-top:1px solid #eee; padding-top:20px;text-align:center;">
课题联系人：吴勇
</div>
""", unsafe_allow_html=True)
