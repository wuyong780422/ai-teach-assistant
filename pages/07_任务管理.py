import streamlit as st
import os
import pandas as pd
from data_tools import get_all_class, get_all_tasks, add_task, update_task_assign, delete_task, TASK_FILE_DIR

st.set_page_config(page_title="任务管理", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<h1 style='text-align:center;'>班级任务管理中心</h1>", unsafe_allow_html=True)
st.divider()

class_list = get_all_class()

# ========== 一、发布新任务 ==========
st.subheader("一、发布新任务")
task_title = st.text_input("任务标题")
task_content = st.text_area("任务详情（文本说明）", height=120)
upload_files = st.file_uploader(
    "上传附件（支持图片、PDF、Word、Excel、压缩包等，可多选）",
    type=["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "zip", "rar", "txt"],
    accept_multiple_files=True
)
assign_class = st.multiselect("分配给哪些班级", class_list, default=class_list)
deadline = st.text_input("截止时间（可选，格式如：2026-06-30 18:00）", value="")

if st.button("发布任务", type="primary", use_container_width=True):
    if not task_title.strip():
        st.warning("请填写任务标题")
    elif len(assign_class) == 0:
        st.warning("请至少选择一个分配班级")
    else:
        # 保存上传的文件
        saved_names = []
        if upload_files:
            for f in upload_files:
                # 文件名加前缀避免重名
                save_name = f"{task_title}_{f.name}"
                save_path = os.path.join(TASK_FILE_DIR, save_name)
                with open(save_path, "wb") as fp:
                    fp.write(f.getbuffer())
                saved_names.append(save_name)
        # 写入任务记录
        new_id = add_task(task_title.strip(), task_content.strip(), saved_names, assign_class, deadline.strip())
        st.success(f"任务发布成功！任务ID：{new_id}")
        st.rerun()

st.divider()

# ========== 二、已有任务列表 ==========
st.subheader("二、已有任务列表")
task_list = get_all_tasks()
if len(task_list) == 0:
    st.info("暂无发布的任务")
else:
    df = pd.DataFrame(task_list)
    df_show = df[["task_id", "task_title", "assign_class", "deadline", "create_time"]].copy()
    df_show.columns = ["任务ID", "任务标题", "分配班级", "截止时间", "发布时间"]
    st.dataframe(df_show, use_container_width=True)

st.divider()

# ========== 三、修改分配/删除任务 ==========
st.subheader("三、修改分配 & 删除任务")
if len(task_list) == 0:
    st.info("暂无任务可操作")
else:
    task_map = {t["task_id"]: f"{t['task_title']}（{t['task_id']}）" for t in task_list}
    select_task = st.selectbox("选择任务", list(task_map.keys()), format_func=lambda x: task_map[x])
    current_task = next(t for t in task_list if t["task_id"] == select_task)
    current_assign = str(current_task["assign_class"]).split(",")

    col1, col2 = st.columns([3, 1])
    with col1:
        new_assign = st.multiselect("重新选择分配班级", class_list, default=current_assign)
    with col2:
        st.write(" ")
        st.write(" ")
        if st.button("保存分配", type="primary", use_container_width=True):
            if len(new_assign) == 0:
                st.error("至少保留一个班级")
            else:
                update_task_assign(select_task, new_assign)
                st.success("分配修改成功")
                st.rerun()

    if st.button("删除该任务", use_container_width=True):
        delete_task(select_task)
        st.success("任务已删除，附件同步清理")
        st.rerun()

st.divider()
st.page_link("pages/00_教师入口首页.py", label="← 返回教师首页", use_container_width=True)