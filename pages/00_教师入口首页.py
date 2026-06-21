import streamlit as st

# 页面初始化配置
st.set_page_config(page_title="教师入口功能", layout="centered", initial_sidebar_state="collapsed")

# 页面标题，直接渲染文字
st.header("教师入口首页")
st.divider()
# 新增：创建班级功能入口
st.page_link("pages/00_创建班级.py", label="📚 创建班级", use_container_width=True)
# AI备课跳转按钮
st.page_link("pages/01_教师备课助手.py", label="📚 备课功能", use_container_width=True)
# 返回首页按钮
st.divider()
st.page_link("Home.py", label="← 返回系统首页", use_container_width=True)