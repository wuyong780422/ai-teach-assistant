import streamlit as st
import pandas as pd
import os
from data_tools import get_question_list

# 读取测试二题库
test2_questions = get_question_list("test2")
CURRENT_TEST_ID = "test2"

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
.analysis-card {
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

SCORE_CSV = "score_data.csv"
ENCODING = "utf-8-sig"

# 读取登录信息
stu_name = st.session_state.get("stu_name", "")
stu_class = st.session_state.get("stu_class", "")

# 未登录拦截
if not stu_name or not stu_class:
    st.warning("请先返回学生登录页面验证身份后再进入测试！")
    st.page_link("pages/02_学生验证登录.py", label="← 返回学生登录页", use_container_width=True)
    st.stop()

# 初始化答题缓存 & 提交标记
if "ans_cache" not in st.session_state:
    st.session_state.ans_cache = {}
if "is_submit_done" not in st.session_state:
    st.session_state.is_submit_done = False
if "total_score" not in st.session_state:
    st.session_state.total_score = 0
if "level_text" not in st.session_state:
    st.session_state.level_text = ""

# 检查是否数据库已存在该生本次试卷记录（永久禁止重复提交）
has_submit_record = False
if os.path.exists(SCORE_CSV):
    df_score = pd.read_csv(SCORE_CSV, encoding=ENCODING)
    if "test_id" in df_score.columns:
        exist = df_score[(df_score["student_name"] == stu_name) & (df_score["class_name"] == stu_class) & (df_score["test_id"] == CURRENT_TEST_ID)]
        if not exist.empty:
            has_submit_record = True
            st.info("你已完成本次测试，不可重复作答！")
            st.dataframe(exist, use_container_width=True)
            st.page_link("pages/02_学生验证登录.py", label="返回学生主页", use_container_width=True)
            st.stop()

# 重新答题函数：清空缓存
def reset_answer():
    st.session_state.ans_cache = {}
    st.session_state.is_submit_done = False
    st.session_state.total_score = 0
    st.session_state.level_text = ""

# 页面标题
st.markdown("<h1 style='text-align:center;'>测试二答题卷</h1>", unsafe_allow_html=True)
st.divider()

# 未提交：渲染答题界面
if not st.session_state.is_submit_done:
    # 渲染所有题目
    for q in test2_questions:
        qid = q["id"]
        st.markdown(f"### 第{qid}题（满分{q['score']}分）")
        st.write(f"题干：{q['title']}")

        if q["type"] == "single":
            # 单选取消默认选中
            sel = st.radio(label="", options=q["opts"], key=f"q_{qid}", index=None)
            if sel is not None:
                st.session_state.ans_cache[qid] = sel.split(".")[0]
            else:
                st.session_state.ans_cache[qid] = None
        else:
            # 多选
            sel_list = st.multiselect(label="", options=q["opts"], key=f"q_{qid}")
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
                if sorted(user_ans if user_ans else []) == sorted(std_ans):
                    score = q["score"]
            total += score
            q_score_dict[f"q{qid}"] = score

            # 存储原始作答
            if isinstance(user_ans, list):
                user_ans_record[f"user_ans_{qid}"] = ",".join(user_ans)
            else:
                user_ans_record[f"user_ans_{qid}"] = user_ans if user_ans else ""

        # 划分成绩等级
        if total >= 70:
            level = "优秀"
        elif total >= 50:
            level = "良好"
        elif total >= 30:
            level = "合格"
        else:
            level = "不及格"

        # 存入会话用于解析展示
        st.session_state.total_score = total
        st.session_state.level_text = level
        st.session_state.is_submit_done = True

        # 组装存储行写入CSV
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

# 已提交：展示成绩+完整解析
else:
    st.success(f"提交成功！你的总分：{st.session_state.total_score}，等级：{st.session_state.level_text}")
    st.info("下方为全部题目详细作答解析")
    st.divider()

    # 逐题展示完整解析卡片
    for q in test2_questions:
        qid = q["id"]
        user_ans_raw = st.session_state.ans_cache[qid]
        std_ans = q["ans"]

        # 格式化学生答案文本
        if q["type"] == "single":
            stu_ans_text = user_ans_raw if user_ans_raw else "未作答"
            std_ans_text = std_ans
        else:
            stu_ans_text = "、".join(user_ans_raw) if (user_ans_raw and len(user_ans_raw) > 0) else "未作答"
            std_ans_text = "、".join(std_ans)

        # 判断正误
        is_right = False
        if q["type"] == "single":
            is_right = (user_ans_raw == std_ans)
        else:
            is_right = sorted(user_ans_raw if user_ans_raw else []) == sorted(std_ans)

        # 解析卡片
        with st.container(border=True):
            st.subheader(f"第{qid}题（满分{q['score']}分） {'✅回答正确' if is_right else '❌回答错误'}")
            st.write(f"**题干：** {q['title']}")
            st.write(f"**全部选项：** {' | '.join(q['opts'])}")
            st.write(f"**你的答案：** {stu_ans_text}")
            st.write(f"**参考答案：** {std_ans_text}")
            st.write(f"**题目解析：** {q['analysis']}")
    st.divider()

    # 新增重新答题按钮（清空本次作答缓存，仅本次页面可重答，刷新后失效）
    st.button("重新答题", on_click=reset_answer, type="secondary")
    st.page_link("pages/02_学生验证登录.py", label="返回学生主页", use_container_width=True)

# 底部返回
st.divider()
st.page_link("pages/02_学生验证登录.py", label="← 返回学生登录页面", use_container_width=True)