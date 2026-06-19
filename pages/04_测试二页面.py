import streamlit as st
import pandas as pd
import os
from data_tools import get_question_list

# 读取测试二题库 关键：test2
test2_questions = get_question_list("test2")

st.set_page_config(page_title="测试二答题页面", layout="wide", initial_sidebar_state="collapsed")

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
CURRENT_TEST_ID = "test2"

# 读取登录信息
stu_name = st.session_state.get("stu_name", "")
stu_class = st.session_state.get("stu_class", "")

# 未登录拦截
if not stu_name or not stu_class:
    st.warning("请先返回学生登录页面验证身份后再进入测试！")
    st.page_link("pages/02_学生验证登录.py", label="← 返回学生登录页", use_container_width=True)
    st.stop()

# 检查是否已经提交过【测试二】试卷（关键：匹配test2）
submitted = False
if os.path.exists(SCORE_CSV):
    df_score = pd.read_csv(SCORE_CSV, encoding=ENCODING)
    # 双重匹配：学生+班级+当前试卷test2
    exist = df_score[(df_score["student_name"] == stu_name) & (df_score["class_name"] == stu_class) & (df_score["test_id"] == CURRENT_TEST_ID)]
    if not exist.empty:
        submitted = True
        st.info("你已完成测试二，不可重复作答！")
        st.dataframe(exist, use_container_width=True)
        st.page_link("pages/02_学生验证登录.py", label="返回学生主页", use_container_width=True)
        st.stop()

# 初始化答题缓存
if "ans_cache" not in st.session_state:
    st.session_state.ans_cache = {}

# 页面标题
st.markdown("<h1 style='text-align:center;'>测试二答题卷</h1>", unsafe_allow_html=True)
st.divider()

# 渲染所有题目（循环test2题库）
for q in test2_questions:
    qid = q["id"]
    st.markdown(f"### 第{qid}题（满分{q['score']}分）")
    st.write(f"题干：{q['title']}")

    if q["type"] == "single":
        # 单选取消默认选中
        sel = st.radio(label="", options=q["opts"], key=f"q_test2_{qid}", index=None)
        if sel is not None:
            st.session_state.ans_cache[qid] = sel.split(".")[0]
        else:
            st.session_state.ans_cache[qid] = None
    else:
        # 多选
        sel_list = st.multiselect(label="", options=q["opts"], key=f"q_test2_{qid}")
        st.session_state.ans_cache[qid] = [i.split(".")[0] for i in sel_list]
    st.divider()

# 提交按钮
submit_btn = st.button("提交试卷", type="primary")
if submit_btn:
    total = 0
    q_score_dict = {}
    user_ans_record = {}

    for q in test2_questions:
        qid = q["id"]
        user_ans = st.session_state.ans_cache[qid]
        std_ans = q["ans"]
        score = 0

        if q["type"] == "single":
            if user_ans == std_ans:
                score = q["score"]
        else:
            if sorted(user_ans) == sorted(std_ans):
                score = q["score"]
        total += score
        q_score_dict[f"q{qid}"] = score

        # 存储原始作答
        if isinstance(user_ans, list):
            user_ans_record[f"user_ans_{qid}"] = ",".join(user_ans)
        else:
            user_ans_record[f"user_ans_{qid}"] = user_ans

    # 划分成绩等级
    if total >= 70:
        level = "优秀"
    elif total >= 50:
        level = "良好"
    elif total >= 30:
        level = "合格"
    else:
        level = "不及格"

    # 组装存储行 关键：test_id固定test2
    row_data = {
        "student_name": stu_name.strip(),
        "class_name": stu_class.strip(),
        "test_id": CURRENT_TEST_ID,
        "total_score": total,
        "level": level,
        **q_score_dict,
        **user_ans_record
    }

    # 写入CSV成绩文件
    df_new = pd.DataFrame([row_data])
    if os.path.exists(SCORE_CSV):
        df_old = pd.read_csv(SCORE_CSV, encoding=ENCODING)
        df_save = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_save = df_new
    df_save.to_csv(SCORE_CSV, index=False, encoding=ENCODING)

    st.success(f"提交成功！你的总分：{total}，等级：{level}")
    st.info("刷新页面或返回登录页可查看成绩，无法再次答题")
    st.page_link("pages/02_学生验证登录.py", label="返回学生主页", use_container_width=True)

# 返回学生登录页
st.divider()
st.page_link("pages/02_学生验证登录.py", label="← 返回学生登录页面", use_container_width=True)