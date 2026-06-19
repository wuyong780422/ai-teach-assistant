import streamlit as st
import pandas as pd
import os
from data_tools import add_class, get_all_class, get_students_by_class, get_class_all_info, get_question_list

st.set_page_config(page_title="创建班级", layout="centered", initial_sidebar_state="collapsed")
st.markdown("<h1 style='text-align:center;'>创建班级</h1>", unsafe_allow_html=True)
st.divider()

# ===================== 常量配置 =====================
SCORE_CSV = "score_data.csv"
ENCODING = "utf-8-sig"

# 1、创建班级区域
st.subheader("新建班级")
new_class = st.text_input("输入班级名称（例：高一1班）")
if st.button("确认创建班级"):
    if new_class.strip() == "":
        st.warning("班级名称不能为空！")
    else:
        flag, msg = add_class(new_class.strip())
        if flag:
            st.success(f"创建成功！班级：{new_class}，班级验证码：{msg}")
        else:
            st.error(msg)
st.divider()

# 2、选择班级，查看本班学生 + 显示该班验证码
st.subheader("查看班级学生")
class_list = get_all_class()
class_info = get_class_all_info()
select_class = ""
if len(class_list) == 0:
    st.info("暂无班级，请先创建班级")
else:
    select_class = st.selectbox("选择班级", class_list)
    # 展示当前选中班级的验证码
    show_code = class_info[select_class]
    st.info(f"当前班级【{select_class}】验证码：{show_code}")
    student_list = get_students_by_class(select_class)
    st.write(f"【{select_class}】已加入学生：")
    if len(student_list) == 0:
        st.info("暂无学生加入该班级")
    else:
        # 每行8列排版
        total = len(student_list)
        row_num = (total + 7) // 8
        idx = 0
        for _ in range(row_num):
            cols = st.columns(8)
            for c in cols:
                if idx < total:
                    c.button(student_list[idx], use_container_width=True)
                    idx += 1

# ===================== 本班成绩专项分析（支持切换测试一/测试二） =====================
st.divider()
st.subheader("📊 班级试卷成绩分析")

# 试卷映射
test_map = {
    "test1": "测试一",
    "test2": "测试二"
}
selected_test_id = st.selectbox("选择需要分析的试卷", options=list(test_map.keys()), format_func=lambda k: test_map[k])
# 动态读取题库
current_questions = get_question_list(selected_test_id)

if not select_class:
    st.info("请先在上方【选择班级】下拉框选中班级，再加载成绩分析")
elif len(current_questions) == 0:
    st.warning(f"{test_map[selected_test_id]} 题库为空，请检查question_bank.csv配置")
else:
    st.write(f"待分析班级：{select_class} | 当前试卷：{test_map[selected_test_id]}")
    start_analysis = st.button("加载本班对应试卷成绩数据", type="primary")

    if start_analysis:
        df_score = pd.DataFrame()
        if os.path.exists(SCORE_CSV):
            df_score = pd.read_csv(SCORE_CSV, encoding=ENCODING)
        else:
            st.warning("score_data.csv 成绩文件不存在，暂无成绩数据")

        if df_score.empty:
            st.warning("系统暂无任何试卷提交记录")
        else:
            # 双重筛选：班级 + 当前试卷ID（核心修复）
            if "test_id" not in df_score.columns:
                st.warning("旧成绩无试卷区分字段，请重新提交试卷生成test_id数据")
                class_score = pd.DataFrame()
            else:
                class_score = df_score[
                    (df_score["class_name"] == select_class) & (df_score["test_id"] == selected_test_id)].copy()

            if class_score.empty:
                st.warning(f"【{select_class}】暂无学生提交{test_map[selected_test_id]}试卷")
            else:
                total_part = len(class_score)
                # 班级整体汇总
                st.subheader("一、班级整体概况")
                avg_score = round(class_score["total_score"].mean(), 2)
                max_s = class_score["total_score"].max()
                min_s = class_score["total_score"].min()

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("参与测试人数", total_part)
                with c2:
                    st.metric("班级平均分", avg_score)
                with c3:
                    st.metric("最高分", max_s)
                with c4:
                    st.metric("最低分", min_s)

                st.subheader("成绩等级分布统计")
                level_count = class_score["level"].value_counts()
                st.dataframe(level_count, use_container_width=True)
                st.divider()

                # 逐题分析
                st.subheader("二、逐题作答详情与选项分布")
                for q in current_questions:
                    qid = q["id"]
                    score_col = f"q{qid}"
                    ans_col = f"user_ans_{qid}"

                    st.markdown(f"### 第{qid}题（满分{q['score']}分）")
                    st.write(f"**题目：** {q['title']}")
                    st.write(f"**全部选项：** {' | '.join(q['opts'])}")
                    std_ans_str = "、".join(q["ans"]) if isinstance(q["ans"], list) else q["ans"]
                    st.write(f"**参考答案：** {std_ans_str}")

                    q_avg = round(class_score[score_col].mean(), 2)
                    right_num = len(class_score[class_score[score_col] == q["score"]])
                    wrong_num = total_part - right_num
                    accuracy = round(right_num / total_part * 100, 2)
                    error_rate = round(wrong_num / total_part * 100, 2)
                    st.write(
                        f"班级本题平均分：{q_avg} | 答对人数：{right_num}/{total_part} | 正确率：{accuracy}% | 错误率：{error_rate}%")

                    if q["type"] == "single":
                        abcd_count = {"A": 0, "B": 0, "C": 0, "D": 0}
                        if ans_col in class_score.columns:
                            valid_ans = class_score[ans_col].dropna()
                            for ans in valid_ans:
                                if ans in abcd_count:
                                    abcd_count[ans] += 1
                        bar_df = pd.DataFrame({
                            "选项": list(abcd_count.keys()),
                            "选择人数": list(abcd_count.values())
                        })
                        st.bar_chart(bar_df, x="选项", y="选择人数", height=240, use_container_width=True)
                    else:
                        bar_df = pd.DataFrame({
                            "答题情况": ["答对人数", "答错人数"],
                            "人数": [right_num, wrong_num]
                        })
                        st.bar_chart(bar_df, x="答题情况", y="人数", height=240, use_container_width=True)
                    st.divider()

# 返回教师首页
st.divider()
st.page_link("pages/00_教师入口首页.py", label="← 返回教师入口功能", use_container_width=True)