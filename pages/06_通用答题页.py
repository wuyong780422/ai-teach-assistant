import streamlit as st
import pandas as pd
import os
from data_tools import get_question_list, auto_paper_point, is_paper_finished, get_class_papers

st.set_page_config(page_title="在线答题", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
a[data-testid="stPageLink"] {font-size:18px; font-weight:500;}
</style>
""", unsafe_allow_html=True)

SCORE_CSV = "score_data.csv"
CODE = "utf-8-sig"

# 获取当前试卷与学生信息
paper_id = st.session_state.get("current_paper_id", "")
stu_name = st.session_state.get("stu_name", "")
stu_class = st.session_state.get("stu_class", "")

# 登录校验
if not paper_id or not stu_name or not stu_class:
    st.warning("请先登录学生账号并选择试卷！")
    st.page_link("pages/02_学生验证登录.py", label="返回登录页", use_container_width=True)
    st.stop()

# 加载题目与试卷名称
q_list = get_question_list(paper_id)
paper_name = ""
for p in get_class_papers(stu_class):
    if p["paper_id"] == paper_id:
        paper_name = p["paper_name"]
        break

# 会话缓存初始化
cache_ans = f"ans_{paper_id}"
cache_submit = f"sub_{paper_id}"
cache_score = f"scr_{paper_id}"
cache_level = f"lv_{paper_id}"
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

# 防重复作答校验
has_submit = is_paper_finished(stu_name, stu_class, paper_id)
if has_submit and not is_submit:
    st.info("你已完成本次测试，不可重复作答！")
    if os.path.exists(SCORE_CSV):
        df_score = pd.read_csv(SCORE_CSV, encoding=CODE)
        show_df = df_score[(df_score["student_name"] == stu_name) & (df_score["class_name"] == stu_class) & (
                    df_score["test_id"] == paper_id)]
        if not show_df.empty:
            st.dataframe(show_df, use_container_width=True)
    st.page_link("pages/02_学生验证登录.py", label="返回试卷列表", use_container_width=True)
    st.stop()

# 试卷标题
st.markdown(f"<h1 style='text-align:center;'>{paper_name} 答题卷</h1>", unsafe_allow_html=True)
st.divider()

# 答题区
if not is_submit:
    for q in q_list:
        qid = q["id"]
        q_type = q["type"]
        st.markdown(f"### 第{qid}题（{q['score']}分）")
        st.write(f"题干：{q['title']}")

        if q_type == "single":
            sel = st.radio("", options=q["opts"], key=f"p_{paper_id}_q{qid}", index=None)
            user_ans[qid] = sel.split(".")[0] if sel else None
        elif q_type == "multi":
            multi_sel = st.multiselect("", options=q["opts"], key=f"p_{paper_id}_q{qid}")
            user_ans[qid] = [s.split(".")[0] for s in multi_sel]
        elif q_type == "judge":
            sel = st.radio("", options=["对", "错"], key=f"p_{paper_id}_q{qid}", index=None)
            user_ans[qid] = "A" if sel == "对" else ("B" if sel == "错" else None)
        elif q_type == "fill":
            fill_ans = st.text_input("请填写答案", key=f"p_{paper_id}_q{qid}")
            user_ans[qid] = fill_ans.strip()
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

            if q["type"] in ["single", "judge"]:
                if ans == std:
                    get_scr = q["score"]
            elif q["type"] == "multi":
                if isinstance(ans, list) and isinstance(std, list):
                    if sorted(ans) == sorted(std):
                        get_scr = q["score"]
            elif q["type"] == "fill":
                if ans:
                    ans_clean = str(ans).strip().lower()
                    std_clean = str(std).strip().lower()
                    # 按 / 分割多个正确答案，自动去除空格
                    std_list = [s.strip() for s in std_clean.split("/")]
                    # 模糊匹配：学生答案包含任一正确答案，或正确答案包含学生答案，均判对
                    is_right = any(s in ans_clean or ans_clean in s for s in std_list)
                    if is_right:
                        get_scr = q["score"]

            total += get_scr
            q_score_dict[f"q{qid}"] = get_scr
            if isinstance(ans, list):
                ans_record[f"user_ans_{qid}"] = ",".join(ans)
            else:
                ans_record[f"user_ans_{qid}"] = ans if ans else ""

        # 统一评级规则
        if total >= 80:
            level = "优秀"
        elif total >= 70:
            level = "良好"
        elif total >= 60:
            level = "及格"
        else:
            level = "不及格"

        st.session_state[cache_score] = total
        st.session_state[cache_level] = level
        st.session_state[cache_submit] = True

        # 写入成绩表
        row_data = {
            "student_name": stu_name,
            "class_name": stu_class,
            "test_id": paper_id,
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

        # 统一发放积分
        flag, msg = auto_paper_point(stu_class, stu_name, paper_id, level)
        if flag:
            st.success(f"试卷积分自动发放成功：{msg}")
        else:
            st.info(msg)
        st.rerun()

# 提交后结果展示
else:
    st.success(f"提交完成！总分：{total_scr}，评级：{level_txt}")
    st.info("提交后无法修改，下方为全部题目解析")
    st.divider()

    for q in q_list:
        qid = q["id"]
        user_ans_raw = user_ans.get(qid, None)
        std_ans = q["ans"]
        q_type = q["type"]

        if q_type == "single":
            stu_txt = user_ans_raw if user_ans_raw else "未作答"
            std_txt = std_ans
            right = (user_ans_raw == std_ans)
        elif q_type == "multi":
            stu_txt = "、".join(user_ans_raw) if (user_ans_raw and len(user_ans_raw) > 0) else "未作答"
            std_txt = "、".join(std_ans)
            right = sorted(user_ans_raw if user_ans_raw else []) == sorted(std_ans)
        elif q_type == "judge":
            # A/B转成对/错显示
            stu_txt = "对" if user_ans_raw == "A" else ("错" if user_ans_raw == "B" else "未作答")
            std_txt = "对" if std_ans == "A" else "错"
            right = (user_ans_raw == std_ans)
        else:
            stu_txt = user_ans_raw if user_ans_raw else "未作答"
            std_txt = std_ans
            # 同步多答案判断逻辑，和判分保持一致
            ans_clean = str(user_ans_raw).strip().lower() if user_ans_raw else ""
            std_clean = str(std_ans).strip().lower()
            std_list = [s.strip() for s in std_clean.split("/")]
            right = ans_clean != "" and any(s in ans_clean or ans_clean in s for s in std_list)

        with st.container(border=True):
            st.subheader(f"第{qid}题（{q['score']}分） {'✅正确' if right else '❌错误'}")
            st.write(f"题干：{q['title']}")
            if q_type in ["single", "multi", "judge"]:
                st.write(f"选项：{' | '.join(q['opts'])}")
            st.write(f"你的答案：{stu_txt}")
            st.write(f"标准答案：{std_txt}")
            st.write(f"解析：{q['analysis']}")
    st.divider()
    st.page_link("pages/02_学生验证登录.py", label="返回试卷列表", use_container_width=True)

st.divider()
st.page_link("pages/02_学生验证登录.py", label="← 返回登录页面", use_container_width=True)