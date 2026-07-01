import streamlit as st

st.set_page_config(page_title="教师入口功能", layout="centered", initial_sidebar_state="collapsed")

# 初始化验证状态
if "teacher_verified" not in st.session_state:
    st.session_state["teacher_verified"] = False

# ========== 未验证：显示验证码输入 ==========
if not st.session_state["teacher_verified"]:
    st.markdown("<h1 style='text-align:center;'>教师入口验证</h1>", unsafe_allow_html=True)
    st.divider()

    input_code = st.text_input("请输入教师入口验证码", type="password")
    if st.button("确认进入", type="primary", use_container_width=True):
        if input_code.strip() == "8888":
            st.session_state["teacher_verified"] = True
            st.rerun()
        else:
            st.error("验证码错误，请重新输入")

    st.divider()
    st.page_link("Home.py", label="← 返回系统首页", use_container_width=True)
    st.stop()

# ========== 验证通过：显示原有功能菜单 ==========
st.header("教师入口首页")
st.divider()
st.page_link("pages/00_创建班级.py", label="📚 班级管理", use_container_width=True)
st.page_link("pages/05_试卷管理.py", label="📚 试卷管理", use_container_width=True)
st.page_link("pages/07_任务管理.py", label="📚 任务管理", use_container_width=True)
st.page_link("pages/08_资源管理.py", label="📚 资源管理", use_container_width=True)
st.page_link("pages/01_教师备课助手.py", label="📚 备课功能", use_container_width=True)
st.divider()
st.page_link("Home.py", label="← 返回系统首页", use_container_width=True)