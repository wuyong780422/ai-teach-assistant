import streamlit as st
import pandas as pd
from data_tools import get_all_class, add_new_paper, add_question, get_all_papers

st.set_page_config(page_title="试卷管理", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<h1 style='text-align:center;'>试卷管理中心</h1>", unsafe_allow_html=True)
st.divider()

if "step" not in st.session_state:
    st.session_state["step"] = 1
if "paper_base" not in st.session_state:
    st.session_state["paper_base"] = {}

# ========== 第一步：试卷基本信息 ==========
if st.session_state["step"] == 1:
    st.subheader("一、试卷基本信息")
    paper_name = st.text_input("试卷名称", value="单元测试卷")
    class_list = get_all_class()
    assign_class = st.multiselect("分配给哪些班级", class_list, default=class_list)
    q_count = st.number_input("题目数量（总分100分）", min_value=5, max_value=50, value=20, step=1)

    if st.button("下一步：录入题目", type="primary", use_container_width=True):
        if not paper_name.strip():
            st.warning("请填写试卷名称")
        elif len(assign_class) == 0:
            st.warning("请至少选择一个分配班级")
        else:
            per_score = round(100 / int(q_count), 2)
            st.session_state["paper_base"] = {
                "name": paper_name.strip(),
                "count": int(q_count),
                "assign": assign_class,
                "per_score": per_score
            }
            st.session_state["step"] = 2
            st.rerun()
    st.divider()

    st.subheader("二、已有试卷列表")
    papers = get_all_papers()
    if len(papers) == 0:
        st.info("暂无试卷")
    else:
        df = pd.DataFrame(papers)
        df = df[["paper_id", "paper_name", "total_score", "question_count", "assign_class", "create_time"]]
        df.columns = ["试卷ID", "试卷名称", "总分", "题目数", "分配班级", "创建时间"]
        st.dataframe(df, use_container_width=True)

    st.divider()

    # ========== 修改分配 + 删除试卷 ==========
    st.subheader("三、修改分配 & 删除试卷")
    if len(papers) == 0:
        st.info("暂无试卷可操作")
    else:
        paper_id_map = {p["paper_id"]: f"{p['paper_name']}（{p['paper_id']}）" for p in papers}
        select_paper = st.selectbox("选择要操作的试卷", list(paper_id_map.keys()),
                                    format_func=lambda x: paper_id_map[x])
        current_paper = next(p for p in papers if p["paper_id"] == select_paper)
        current_assign = str(current_paper["assign_class"]).split(",") if current_paper[
                                                                              "assign_class"] != "all" else class_list
        new_assign = st.multiselect("重新选择分配班级", class_list, default=current_assign)

        col_save, col_del = st.columns(2)
        with col_save:
            if st.button("保存分配设置", type="primary", use_container_width=True):
                if len(new_assign) == 0:
                    st.error("请至少保留一个分配班级")
                else:
                    PAPER_CSV = "paper_info.csv"
                    df_paper = pd.read_csv(PAPER_CSV, encoding="utf-8-sig")
                    assign_str = ",".join(new_assign)
                    df_paper.loc[df_paper["paper_id"] == select_paper, "assign_class"] = assign_str
                    df_paper.to_csv(PAPER_CSV, index=False, encoding="utf-8-sig")
                    st.success("分配班级修改成功，学生端刷新后立即生效")
                    st.rerun()

        with col_del:
            if st.button("删除该试卷", use_container_width=True):
                # 1. 删除试卷主记录
                PAPER_CSV = "paper_info.csv"
                df_paper = pd.read_csv(PAPER_CSV, encoding="utf-8-sig")
                df_paper = df_paper[df_paper["paper_id"] != select_paper]
                df_paper.to_csv(PAPER_CSV, index=False, encoding="utf-8-sig")

                # 2. 删除对应所有题目
                QUESTION_CSV = "question_bank.csv"
                df_q = pd.read_csv(QUESTION_CSV, encoding="utf-8-sig")
                df_q = df_q[df_q["test_id"] != select_paper]
                df_q.to_csv(QUESTION_CSV, index=False, encoding="utf-8-sig")

                st.success("试卷及对应题目已删除")
                st.rerun()

# ========== 第二步：逐题录入 ==========
else:
    base = st.session_state["paper_base"]
    st.subheader(f"录入题目：{base['name']}（共{base['count']}题，每题{base['per_score']}分）")
    st.info("支持单选题、多选题、判断题、填空题，填写完成后点击底部保存")
    st.divider()

    q_data = []
    for i in range(1, base["count"] + 1):
        st.markdown(f"### 第{i}题")
        q_type = st.selectbox("题型", ["单选题", "多选题", "判断题", "填空题"], key=f"type_{i}")
        q_title = st.text_input("题干", key=f"title_{i}")

        if q_type in ["单选题", "多选题"]:
            c1, c2 = st.columns(2)
            opt_a = c1.text_input("选项A", key=f"a_{i}")
            opt_b = c2.text_input("选项B", key=f"b_{i}")
            c3, c4 = st.columns(2)
            opt_c = c3.text_input("选项C", key=f"c_{i}")
            opt_d = c4.text_input("选项D", key=f"d_{i}")

            if q_type == "单选题":
                ans = st.selectbox("正确答案", ["A", "B", "C", "D"], key=f"ans_{i}")
            else:
                ans = st.multiselect("正确答案（多选）", ["A", "B", "C", "D"], key=f"ans_{i}")
            analysis = st.text_input("答案解析", key=f"ana_{i}")
            q_data.append({
                "id": i, "type": "single" if q_type == "单选题" else "multi",
                "title": q_title, "a": opt_a, "b": opt_b, "c": opt_c, "d": opt_d,
                "ans": ans, "analysis": analysis
            })

        elif q_type == "判断题":
            ans_label = st.selectbox("正确答案", ["对", "错"], key=f"ans_{i}")
            analysis = st.text_input("答案解析", key=f"ana_{i}")
            opt_a, opt_b, opt_c, opt_d = "对", "错", "", ""
            ans_val = "A" if ans_label == "对" else "B"
            q_data.append({
                "id": i, "type": "judge",
                "title": q_title, "a": opt_a, "b": opt_b, "c": opt_c, "d": opt_d,
                "ans": ans_val, "analysis": analysis
            })

        else:
            ans = st.text_input("标准答案", key=f"ans_{i}")
            analysis = st.text_input("答案解析", key=f"ana_{i}")
            q_data.append({
                "id": i, "type": "fill",
                "title": q_title, "a": "", "b": "", "c": "", "d": "",
                "ans": ans, "analysis": analysis
            })
        st.divider()

    col_back, col_save = st.columns(2)
    with col_back:
        if st.button("返回上一步", use_container_width=True):
            st.session_state["step"] = 1
            st.rerun()
    with col_save:
        if st.button("保存试卷", type="primary", use_container_width=True):
            empty_flag = False
            for q in q_data:
                if not q["title"].strip():
                    empty_flag = True
                    break
                if q["type"] in ["single", "multi"]:
                    if not q["a"].strip() or not q["b"].strip() or not q["c"].strip() or not q["d"].strip():
                        empty_flag = True
                        break
                if q["type"] == "fill" and not q["ans"].strip():
                    empty_flag = True
                    break
            if empty_flag:
                st.error("题干和必填选项不能为空，请检查填写")
            else:
                paper_id = add_new_paper(base["name"], base["count"], base["assign"])
                for q in q_data:
                    add_question(
                        paper_id, q["id"], q["type"], base["per_score"],
                        q["title"], q["a"], q["b"], q["c"], q["d"],
                        q["ans"], q["analysis"]
                    )
                st.success(f"试卷创建成功！试卷ID：{paper_id}")
                st.session_state["step"] = 1
                st.session_state["paper_base"] = {}
                st.rerun()

st.divider()
st.page_link("pages/00_教师入口首页.py", label="← 返回教师首页", use_container_width=True)