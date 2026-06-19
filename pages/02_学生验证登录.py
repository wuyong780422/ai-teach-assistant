import streamlit as st
from data_tools import get_all_class, add_student, check_class_code
import pandas as pd
import os

st.set_page_config(page_title="学生登录", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<h1 style='text-align:center;'>学生入口验证</h1>", unsafe_allow_html=True)
st.divider()

# 会话缓存初始化
if "stu_name" not in st.session_state:
    st.session_state.stu_name = ""
if "stu_class" not in st.session_state:
    st.session_state.stu_class = ""

SCORE_CSV = "score_data.csv"
ENCODING = "utf-8-sig"

# 根据试卷id判断是否完成作答
def is_test_finished(name, cls, test_id):
    if not os.path.exists(SCORE_CSV):
        return False
    df = pd.read_csv(SCORE_CSV, encoding=ENCODING)
    if "test_id" not in df.columns:
        return False
    df["student_name"] = df["student_name"].astype(str).str.strip()
    df["class_name"] = df["class_name"].astype(str).str.strip()
    target_name = name.strip()
    target_cls = cls.strip()
    match = df[(df["student_name"] == target_name) & (df["class_name"] == target_cls) & (df["test_id"] == test_id)]
    return len(match) > 0

class_list = get_all_class()
pass_flag = False
test1_finish = False
test2_finish = False

if len(class_list) == 0:
    st.error("暂无可用班级，请教师先创建班级")
else:
    select_class = st.selectbox("选择你的班级", class_list)
    input_code = st.text_input("输入班级4位验证码")
    stu_name = st.text_input("输入你的姓名")
    if st.button("进入学生页面"):
        input_code_clean = input_code.strip()
        stu_name_clean = stu_name.strip()
        if input_code_clean == "" or stu_name_clean == "":
            st.warning("验证码和姓名均不能为空！")
        else:
            if not check_class_code(select_class, input_code_clean):
                st.error("验证码错误，请核对班级验证码！")
            else:
                flag, msg = add_student(stu_name_clean, select_class)
                st.session_state.stu_name = stu_name_clean
                st.session_state.stu_class = select_class
                if flag:
                    st.success(f"{stu_name_clean}，验证通过，已加入{select_class}！")
                else:
                    st.warning(msg)
                pass_flag = True
                # 分别查询两套试卷完成状态
                test1_finish = is_test_finished(stu_name_clean, select_class, "test1")
                test2_finish = is_test_finished(stu_name_clean, select_class, "test2")

if pass_flag:
    st.divider()
    st.subheader("在线测试功能")

    # ========== 测试一 布局（和你截图样式完全一致） ==========
    col_btn1, col_tag1 = st.columns([8, 2])
    with col_btn1:
        with st.container(height=90):
            st.write("")
            st.page_link("pages/03_测试一页面.py", label="📝 测试一", use_container_width=True)
            st.write("")
    with col_tag1:
        with st.container(height=90):
            if test1_finish:
                st.success("已测试")
            else:
                st.info("未测试")

    st.write("") # 空行分隔两套试卷

    # ========== 测试二 同逻辑同布局 ==========
    col_btn2, col_tag2 = st.columns([8, 2])
    with col_btn2:
        with st.container(height=90):
            st.write("")
            st.page_link("pages/04_测试二页面.py", label="📝 测试二", use_container_width=True)
            st.write("")
    with col_tag2:
        with st.container(height=90):
            if test2_finish:
                st.success("已测试")
            else:
                st.info("未测试")

st.divider()
st.page_link("Home.py", label="← 返回系统首页", use_container_width=True)