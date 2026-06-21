import streamlit as st
import pandas as pd
import os
from data_tools import get_question_list, auto_test_point

TEST_ID = "test1"
q_list = get_question_list(TEST_ID)

st.set_page_config(page_title="测试一答题页面", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
a[data-testid="stPageLink"] {font-size:18px; font-weight:500;}
</style>
""", unsafe_allow_html=True)

SCORE_CSV = "score_data.csv"
CODE = "utf-8-sig"

stu_name = st.session_state.get("stu_name", "")
stu_class = st.session_state.get("stu_class", "")
if not stu_name or not stu_class:
    st.warning("请先登录学生账号！")
    st.page_link("pages/02_学生验证登录.py", label="返回登录页", use_container_width=True)
    st.stop()

cache_ans = f"ans_{TEST_ID}"
cache_submit = f"sub_{TEST_ID}"
cache_score = f"scr_{TEST_ID}"
cache_level = f"lv_{TEST_ID}"
if cache_ans not in st.session_state:
    st.session_state[cache_ans] = {}
if cache_submit not in st.session_state:
    st.session_state[cache_submit] = False
if cache_score not in st.session_state:
    st.session_state[cache_score] = 0
if cache_level not in st.session_state:
    st.session_state[cache_level] = ""

user_ans = st.session_state[cache_ans]
is_submit = st.session_state[cache_submit]
total_scr = st.session_state[cache_score]
level_txt = st.session_state[cache_level]

has_submit = False
if os.path.exists(SCORE_CSV):
    df_score = pd.read_csv(SCORE_CSV, encoding=CODE)
    if "test_id" in df_score.columns:
        filter_row = df_score[(df_score["student_name"] == stu_name) & (df_score["class_name"] == stu_class) & (df_score["test_id"] == TEST_ID)]
        has_submit = len(filter_row) > 0
if has_submit and not is_submit:
    st.info("你已完成本次测试，不可重复作答！")
    show_df = df_score[(df_score["student_name"] == stu_name) & (df_score["class_name"] == stu_class) & (df_score["test_id"] == TEST_ID)]
    st.dataframe(show_df, use_container_width=True)
    st.page_link("pages/02_学生验证登录.py", label="返回学生主页", use_container_width=True)
    st.stop()

st.markdown("<h1 style='text-align:center;'>测试一答题卷</h1>", unsafe_allow_html=True)
st.divider()

if not is_submit:
    st.button("清空全部答案重新作答", on_click=lambda: st.session_state.update({cache_ans:{}}), type="secondary")
    st.divider()
    for q in q_list:
        qid = q["id"]
        st.markdown(f"### 第{qid}题（{q['score']}分）")
        st.write(f"题干：{q['title']}")
        if q["type"] == "single":
            sel = st.radio("", options=q["opts"], key=f"t1_q{qid}", index=None)
            user_ans[qid] = sel.split(".")[0] if sel else None
        else:
            multi_sel = st.multiselect("", options=q["opts"], key=f"t1_m{qid}")
            user_ans[qid] = [i.split(".")[0] for i in multi_sel]
        st.divider()
    submit_btn = st.button("提交试卷", type="primary")
    if submit_btn:
        total = 0
        q_score_dict = {}
        ans_record = {}
        for q in q_list:
            qid = q["id"]
            ans = user_ans.get(qid, None)
            std = q["ans"]
            get_scr = 0
            if q["type"] == "single":
                if ans == std:
                    get_scr = q["score"]
            else:
                if sorted(ans if ans else []) == sorted(std):
                    get_scr = q["score"]
            total += get_scr
            q_score_dict[f"q{qid}"] = get_scr
            if isinstance(ans, list):
                ans_record[f"user_ans_{qid}"] = ",".join(ans)
            else:
                ans_record[f"user_ans_{qid}"] = ans if ans else ""
        if total >= 70:
            level = "优秀"
        elif total >= 50:
            level = "良好"
        elif total >= 30:
            level = "及格"
        else:
            level = "不及格"
        st.session_state[cache_score] = total
        st.session_state[cache_level] = level
        st.session_state[cache_submit] = True
        row_data = {
            "student_name": stu_name,
            "class_name": stu_class,
            "test_id": TEST_ID,
            "total_score": total,
            "level": level,
            **q_score_dict,
            **ans_record
        }
        new_df = pd.DataFrame([row_data])
        if os.path.exists(SCORE_CSV):
            old_df = pd.read_csv(SCORE_CSV, encoding=CODE)
            save_df = pd.concat([old_df, new_df], ignore_index=True)
        else:
            save_df = new_df
        save_df.to_csv(SCORE_CSV, index=False, encoding=CODE)
        flag, msg = auto_test_point(stu_class, stu_name, TEST_ID, level)
        if flag:
            st.success(f"试卷积分自动发放成功：{msg}")
        else:
            st.info(msg)
        st.rerun()
else:
    st.success(f"提交完成！总分：{total_scr}，评级：{level_txt}")
    st.info("提交后无法修改，下方为全部题目解析")
    st.divider()
    for q in q_list:
        qid = q["id"]
        user_ans_raw = user_ans.get(qid, None)
        std_ans = q["ans"]
        if q["type"] == "single":
            stu_txt = user_ans_raw if user_ans_raw else "未作答"
            std_txt = std_ans
            right = (user_ans_raw == std_ans)
        else:
            stu_txt = "、".join(user_ans_raw) if (user_ans_raw and len(user_ans_raw)>0) else "未作答"
            std_txt = "、".join(std_ans)
            right = sorted(user_ans_raw if user_ans_raw else []) == sorted(std_ans)
        with st.container(border=True):
            st.subheader(f"第{qid}题（{q['score']}分） {'✅正确' if right else '❌错误'}")
            st.write(f"题干：{q['title']}")
            st.write(f"选项：{' | '.join(q['opts'])}")
            st.write(f"你的答案：{stu_txt}")
            st.write(f"标准答案：{std_txt}")
            st.write(f"解析：{q['analysis']}")
    st.divider()
    st.page_link("pages/02_学生验证登录.py", label="返回学生主页", use_container_width=True)
st.divider()
st.page_link("Home.py", label="← 返回系统首页", use_container_width=True)