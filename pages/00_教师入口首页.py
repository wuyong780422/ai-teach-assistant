import streamlit as st

st.set_page_config(page_title="教师入口功能", layout="centered", initial_sidebar_state="collapsed")
st.header("教师入口首页")
st.divider()

st.page_link("pages/00_创建班级.py", label="📚 班级管理", use_container_width=True)
st.page_link("pages/05_试卷管理.py", label="📚 试卷管理", use_container_width=True)
st.page_link("pages/07_任务管理.py", label="📚 任务管理", use_container_width=True)
st.page_link("pages/01_教师备课助手.py", label="📚 备课功能", use_container_width=True)

st.divider()
st.page_link("Home.py", label="← 返回系统首页", use_container_width=True)