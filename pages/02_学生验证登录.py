import streamlit as st
import pandas as pd
import os
import datetime
from data_tools import get_class_all_info, add_student, get_class_papers, is_paper_finished, get_class_tasks, \
    TASK_FILE_DIR

st.set_page_config(page_title="学生验证登录", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<h1 style='text-align:center;'>学生验证登录</h1>", unsafe_allow_html=True)
st.divider()

# 会话变量初始化
if "stu_name" not in st.session_state:
    st.session_state.stu_name = ""
if "stu_class" not in st.session_state:
    st.session_state.stu_class = ""
if "current_paper_id" not in st.session_state:
    st.session_state.current_paper_id = ""

SCORE_CSV = "score_data.csv"
ENCODING = "utf-8-sig"
class_list = list(get_class_all_info().keys())
pass_flag = False

# 图片格式白名单（自动预览）
IMG_EXT = {"jpg", "jpeg", "png", "gif"}

if len(class_list) == 0:
    st.error("暂无可用班级，请教师先创建班级")
else:
    select_class = st.selectbox("选择你的班级", class_list)
    input_code = st.text_input("输入班级4位验证码")
    stu_name = st.text_input("输入你的姓名")

    if st.button("加入班级"):
        input_code_clean = input_code.strip()
        stu_name_clean = stu_name.strip()
        if input_code_clean == "" or stu_name_clean == "":
            st.warning("验证码和姓名均不能为空！")
        else:
            correct_code = str(get_class_all_info()[select_class])
            if input_code_clean != correct_code:
                st.error("验证码错误，请核对班级验证码！")
            else:
                flag, msg = add_student(select_class, stu_name_clean)
                st.session_state.stu_name = stu_name_clean
                st.session_state.stu_class = select_class
                if flag:
                    st.success(f"{stu_name_clean}，验证通过，已加入{select_class}！")
                else:
                    st.warning(msg)
                pass_flag = True

    # 已登录状态校验
    if st.session_state.stu_name and st.session_state.stu_class:
        pass_flag = True

if pass_flag and st.session_state.stu_name:
    st.divider()

    # ========== 一、班级任务板块（修复分段格式+空值显示） ==========
    st.subheader("一、班级任务")
    task_list = get_class_tasks(st.session_state.stu_class)
    if len(task_list) == 0:
        st.info("暂无班级任务")
    else:
        # 区分进行中/已截止
        now = datetime.datetime.now()
        doing_tasks = []
        end_tasks = []
        for t in task_list:
            if t["deadline"] and pd.notna(t["deadline"]) and str(t["deadline"]).strip() != "":
                try:
                    dl = datetime.datetime.strptime(str(t["deadline"]), "%Y-%m-%d %H:%M")
                    if dl < now:
                        end_tasks.append(t)
                    else:
                        doing_tasks.append(t)
                except:
                    doing_tasks.append(t)
            else:
                doing_tasks.append(t)
        all_show_tasks = doing_tasks + end_tasks

        for task in all_show_tasks:
            is_end = task in end_tasks
            with st.expander(f"📌 {task['task_title']} {'【已截止】' if is_end else ''}", expanded=False):
                # 修复：截止时间空值不显示，避免出现 nan
                caption_text = f"发布时间：{task['create_time']}"
                deadline_val = task.get("deadline", "")
                if deadline_val and pd.notna(deadline_val) and str(deadline_val).strip() != "":
                    caption_text += f" | 截止时间：{deadline_val}"
                st.caption(caption_text)

                # 修复：自动将普通换行转换为 Markdown 分段，保留排版格式
                content_raw = task.get("task_content", "")
                if content_raw and pd.notna(content_raw) and str(content_raw).strip() != "":
                    # 将单个换行替换为两个换行，实现回车即分段
                    format_content = str(content_raw).replace("\n", "\n\n")
                    st.markdown(format_content)

                # 空值安全判断附件
                file_name_raw = task.get("file_name", "")
                has_file = False
                file_names = []
                if file_name_raw is not None and str(file_name_raw).strip() != "" and str(
                        file_name_raw).lower() != "nan":
                    file_names = str(file_name_raw).split(",")
                    has_file = len(file_names) > 0

                if has_file:
                    st.write("**附件资料：**")
                    for fn in file_names:
                        f_path = os.path.join(TASK_FILE_DIR, fn)
                        if not os.path.exists(f_path):
                            continue
                        ext = fn.split(".")[-1].lower()
                        show_name = fn.split("_", 1)[1] if "_" in fn else fn

                        if ext in IMG_EXT:
                            # st.image(f_path, caption=show_name, use_column_width=True)  # use_column_width=True 是旧版写法
                            st.image(f_path, caption=show_name, use_container_width=True)
                        else:
                            with open(f_path, "rb") as fp:
                                file_bytes = fp.read()
                            st.download_button(
                                label=f"📎 下载：{show_name}",
                                data=file_bytes,
                                file_name=show_name,
                                use_container_width=True
                            )
    st.divider()

    # ========== 二、在线测试试卷列表 ==========
    st.subheader("二、在线测试试卷列表")
    paper_list = get_class_papers(st.session_state.stu_class)
    if len(paper_list) == 0:
        st.info("当前班级暂无可用试卷")
    else:
        for paper in paper_list:
            finished = is_paper_finished(st.session_state.stu_name, st.session_state.stu_class, paper["paper_id"])
            col_btn, col_tag = st.columns([8, 2])
            with col_btn:
                with st.container(height=105):
                    st.write("")
                    if st.button(f"📝 {paper['paper_name']}（{paper['question_count']}题，满分{paper['total_score']}分）",
                                 key=f"go_{paper['paper_id']}", use_container_width=True):
                        st.session_state.current_paper_id = paper["paper_id"]
                        st.switch_page("pages/06_通用答题页.py")
                    st.write("")
            with col_tag:
                with st.container(height=105):
                    if finished:
                        st.success("已测试")
                    else:
                        st.info("未测试")

st.divider()
st.page_link("Home.py", label="← 返回系统首页", use_container_width=True)