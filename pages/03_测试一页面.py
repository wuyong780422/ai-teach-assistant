import streamlit as st
import pandas as pd
import os
from data_tools import get_question_list

test1_questions = get_question_list("test1")
CURRENT_TEST_ID = "test1"

st.set_page_config(page_title="测试一答题页面", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.center-box {
    display: flex;
    align-items: center;
    height: 100%;
}
a[data-testid="stPageLink"] {
    font-size: 18px !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

SCORE_CSV = "score_data.csv"
ENCODING = "utf-8-sig"

stu_name = st.session_state.get("stu_name", "")
stu_class = st.session_state.get("stu_class", "")

if not stu_name or not stu_class:
    st.warning("请先返回学生登录页面验证身份后再进入测试！")
    st.page_link("pages/02_学生验证登录.py", label="← 返回学生登录页", use_container_width=True)
    st.stop()

# 试卷独立缓存隔离
cache_key_ans = f"ans_cache_{CURRENT_TEST_ID}"
cache_key_submit = f"is_submit_done_{CURRENT_TEST_ID}"
cache_key_score = f"total_score_{CURRENT_TEST_ID}"
cache_key_level = f"level_text_{CURRENT_TEST_ID}"

# 初始化全部缓存
if cache_key_ans not in st.session_state:
    st.session_state[cache_key_ans] = {}
if cache_key_submit not in st.session_state:
    st.session_state[cache_key_submit] = False
if cache_key_score not in st.session_state:
    st.session_state[cache_key_score] = 0
if cache_key_level not in st.session_state:
    st.session_state[cache_key_level] = ""

ans_cache = st.session_state[cache_key_ans]
is_submit_done = st.session_state[cache_key_submit]
total_score = st.session_state[cache_key_score]
level_text = st.session_state[cache_key_level]

# 判断数据库历史提交记录
history_submit = False
if os.path.exists(SCORE_CSV):
    df_score = pd.read_csv(SCORE_CSV, encoding=ENCODING)
    if "test_id" in df_score.columns:
        filter_df = df_score[(df_score["student_name"] == stu_name) & (df_score["class_name"] == stu_class) & (df_score["test_id"] == CURRENT_TEST_ID)]
        history_submit = len(filter_df) > 0
    else:
        if CURRENT_TEST_ID == "test1":
            filter_df = df_score[(df_score["student_name"] == stu_name) & (df_score["class_name"] == stu_class)]
            history_submit = len(filter_df) > 0

# 历史已提交 + 当前无刚提交标记 → 拦截
if history_submit and not is_submit_done:
    st.info("你已完成本次测试，不可重复作答！")
    df_show = pd.read_csv(SCORE_CSV, encoding=ENCODING)
    if "test_id" in df_show.columns:
        show_df = df_show[(df_show["student_name"] == stu_name) & (df_show["class_name"] == stu_class) & (df_show["test_id"] == CURRENT_TEST_ID)]
    else:
        show_df = df_show[(df_show["student_name"] == stu_name) & (df_show["class_name"] == stu_class)]
    st.dataframe(show_df, use_container_width=True)
    st.page_link("pages/02_学生验证登录.py", label="返回学生主页", use_container_width=True)
    st.stop()

# 页面标题
st.markdown("<h1 style='text-align:center;'>测试一答题卷</h1>", unsafe_allow_html=True)
st.divider()

# 未提交答题界面
if not is_submit_done:
    for q in test1_questions:
        qid = q["id"]
        st.markdown(f"### 第{qid}题（满分{q['score']}分）")
        st.write(f"题干：{q['title']}")
        if q["type"] == "single":
            sel = st.radio("", options=q["opts"], key=f"t1_q{qid}", index=None)
            ans_cache[qid] = sel.split(".")[0] if sel else None
        else:
            sel_list = st.multiselect("", options=q["opts"], key=f"t1_mq{qid}")
            ans_cache[qid] = [i.split(".")[0] for i in sel_list]
        st.divider()

    submit_btn = st.button("提交试卷", type="primary")
    if submit_btn:
        total = 0
        q_score_dict = {}
        user_ans_record = {}
        for q in test1_questions:
            qid = q["id"]
            user_ans = ans_cache.get(qid, None)
            std_ans = q["ans"]
            score = 0
            if q["type"] == "single":
                if user_ans == std_ans:
                    score = q["score"]
            else:
                if sorted(user_ans if user_ans else []) == sorted(std_ans):
                    score = q["score"]
            total += score
            q_score_dict[f"q{qid}"] = score
            if isinstance(user_ans, list):
                user_ans_record[f"user_ans_{qid}"] = ",".join(user_ans)
            else:
                user_ans_record[f"user_ans_{qid}"] = user_ans if user_ans else ""
        # 等级判定
        if total >= 70:
            level = "优秀"
        elif total >= 50:
            level = "良好"
        elif total >= 30:
            level = "合格"
        else:
            level = "不及格"
        st.session_state[cache_key_score] = total
        st.session_state[cache_key_level] = level
        st.session_state[cache_key_submit] = True
        # 写入CSV
        row_data = {
            "student_name": stu_name.strip(),
            "class_name": stu_class.strip(),
            "test_id": CURRENT_TEST_ID,
            "total_score": total,
            "level": level,
            **q_score_dict,
            **user_ans_record
        }
        df_new = pd.DataFrame([row_data])
        if os.path.exists(SCORE_CSV):
            df_old = pd.read_csv(SCORE_CSV, encoding=ENCODING)
            df_save = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_save = df_new
        df_save.to_csv(SCORE_CSV, index=False, encoding=ENCODING)
        st.rerun()
# 提交后解析页面
else:
    st.success(f"提交成功！你的总分：{total_score}，等级：{level_text}")
    st.info("下方为全部题目作答详细解析")
    st.divider()
    for q in test1_questions:
        qid = q["id"]
        user_ans_raw = ans_cache.get(qid, None)
        std_ans = q["ans"]
        if q["type"] == "single":
            stu_text = user_ans_raw if user_ans_raw else "未作答"
            std_text = std_ans
            right_flag = (user_ans_raw == std_ans)
        else:
            stu_text = "、".join(user_ans_raw) if (user_ans_raw and len(user_ans_raw) > 0) else "未作答"
            std_text = "、".join(std_ans)
            right_flag = sorted(user_ans_raw if user_ans_raw else []) == sorted(std_ans)
        with st.container(border=True):
            st.subheader(f"第{qid}题（{q['score']}分） {'✅正确' if right_flag else '❌错误'}")
            st.write(f"题干：{q['title']}")
            st.write(f"全部选项：{' | '.join(q['opts'])}")
            st.write(f"你的答案：{stu_text}")
            st.write(f"标准答案：{std_text}")
            st.write(f"解析：{q['analysis']}")
    st.divider()

# 底部返回入口
st.divider()
st.page_link("pages/02_学生验证登录.py", label="← 返回学生登录页面", use_container_width=True)