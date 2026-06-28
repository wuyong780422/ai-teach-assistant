import streamlit as st
import os
import pandas as pd
from data_tools import get_all_class, get_all_resources, add_resource, update_resource_assign, delete_resource, RESOURCE_FILE_DIR

st.set_page_config(page_title="资源管理", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<h1 style='text-align:center;'>教学资源管理中心</h1>", unsafe_allow_html=True)
st.divider()

class_list = get_all_class()
# 可在线预览的格式白名单
IMG_EXT = {"jpg", "jpeg", "png", "gif"}
VIDEO_EXT = {"mp4", "webm"}

# ========== 左右分栏：左上传 右预览 ==========
col_upload, col_preview = st.columns([1, 1])

with col_upload:
    st.subheader("一、上传新资源")
    res_name = st.text_input("资源名称")
    res_type = st.selectbox("资源分类", ["课件文档", "视频资源", "图片动图", "工具素材"])
    upload_file = st.file_uploader(
        "选择资源文件（支持图片、GIF、视频、Office文档、压缩包等）",
        type=["jpg", "jpeg", "png", "gif", "mp4", "webm",
              "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
              "db", "sql", "zip", "rar", "7z"]
    )
    assign_class = st.multiselect("分配给哪些班级", class_list, default=class_list)

    if st.button("上传并发布", type="primary", use_container_width=True):
        if not res_name.strip():
            st.warning("请填写资源名称")
        elif not upload_file:
            st.warning("请选择上传文件")
        elif len(assign_class) == 0:
            st.warning("请至少选择一个分配班级")
        else:
            save_name = f"{res_name}_{upload_file.name}"
            save_path = os.path.join(RESOURCE_FILE_DIR, save_name)
            with open(save_path, "wb") as fp:
                fp.write(upload_file.getbuffer())
            new_id = add_resource(res_name.strip(), res_type, save_name, assign_class)
            st.success(f"资源上传成功！资源ID：{new_id}")
            st.rerun()

with col_preview:
    st.subheader("二、课堂预览播放")
    res_list = get_all_resources()
    if len(res_list) == 0:
        st.info("暂无上传的资源")
    else:
        res_map = {r["res_id"]: f"{r['res_name']}（{r['res_type']}）" for r in res_list}
        select_res = st.selectbox("选择资源预览", list(res_map.keys()), format_func=lambda x: res_map[x])
        current_res = next(r for r in res_list if r["res_id"] == select_res)
        f_path = os.path.join(RESOURCE_FILE_DIR, current_res["file_name"])
        ext = current_res["file_name"].split(".")[-1].lower()
        show_name = current_res["file_name"].split("_", 1)[1] if "_" in current_res["file_name"] else current_res["file_name"]

        if os.path.exists(f_path):
            if ext in IMG_EXT:
                st.image(f_path, use_container_width=True, caption=show_name)
            elif ext in VIDEO_EXT:
                st.video(f_path)
            else:
                st.info("该格式不支持在线预览，可下载后本地打开")
            # 所有格式统一提供下载按钮
            with open(f_path, "rb") as fp:
                st.download_button(
                    label=f"📥 下载：{show_name}",
                    data=fp.read(),
                    file_name=show_name,
                    use_container_width=True
                )

st.divider()

# ========== 资源列表与管理 ==========
st.subheader("三、资源列表与管理")
if len(res_list) == 0:
    st.info("暂无资源")
else:
    df = pd.DataFrame(res_list)
    df_show = df[["res_id", "res_name", "res_type", "assign_class", "create_time"]].copy()
    df_show.columns = ["资源ID", "资源名称", "分类", "分配班级", "上传时间"]
    st.dataframe(df_show, use_container_width=True)

    st.divider()
    st.subheader("四、修改分配 & 删除资源")
    col_op1, col_op2 = st.columns([3, 1])
    with col_op1:
        select_op_res = st.selectbox("选择要操作的资源", list(res_map.keys()), format_func=lambda x: res_map[x], key="op_res")
        op_res = next(r for r in res_list if r["res_id"] == select_op_res)
        current_assign = str(op_res["assign_class"]).split(",")
        new_assign = st.multiselect("重新选择分配班级", class_list, default=current_assign)
    with col_op2:
        st.write(" ")
        st.write(" ")
        if st.button("保存分配", type="primary", use_container_width=True):
            if len(new_assign) == 0:
                st.error("至少保留一个班级")
            else:
                update_resource_assign(select_op_res, new_assign)
                st.success("分配修改成功")
                st.rerun()
        if st.button("删除该资源", use_container_width=True):
            delete_resource(select_op_res)
            st.success("资源已删除，文件同步清理")
            st.rerun()

st.divider()
st.page_link("pages/00_教师入口首页.py", label="← 返回教师首页", use_container_width=True)