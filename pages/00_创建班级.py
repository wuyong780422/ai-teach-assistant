import streamlit as st
import pandas as pd
import os
from data_tools import add_class, get_all_class, get_students_by_class, get_class_all_info, get_question_list, STUDENT_CSV
from data_tools import init_point_csv, get_class_point, add_class_point, add_group_all_point, get_class_group_map, set_student_group, get_group_point_stat

st.set_page_config(page_title="班级管理", layout="centered", initial_sidebar_state="collapsed")
# 初始化会话变量
if "random_pick_stu" not in st.session_state:
    st.session_state["random_pick_stu"] = ""
if "pick_group" not in st.session_state:
    st.session_state["pick_group"] = ""

st.markdown("<h1 style='text-align:center;'>课堂教学管理</h1>", unsafe_allow_html=True)
st.divider()

SCORE_CSV = "score_data.csv"
ENCODING = "utf-8-sig"
init_point_csv()

# 1. 新建班级
st.subheader("一、班级管理")
input_new_class = st.text_input("输入班级名称（如：24级计算机1班）")
if st.button("确认创建班级", type="secondary"):
    if input_new_class.strip() == "":
        st.warning("班级名称不可为空！")
    else:
        flag, msg = add_class(input_new_class.strip())
        if flag:
            st.success(f"创建成功！验证码：{msg}")
        else:
            st.error(msg)
st.divider()

# 2. 学生分组、抽选加分模块
st.subheader("二、课堂加分操作区")
all_class = get_all_class()
class_dict = get_class_all_info()
selected_class = ""
if len(all_class) == 0:
    st.info("暂无班级，请先创建班级")
else:
    selected_class = st.selectbox("选择操作班级", all_class)
    st.info(f"当前班级验证码：{class_dict[selected_class]}")
    stu_list = get_students_by_class(selected_class)
    group_map = get_class_group_map(selected_class)
    group_list = list(group_map.keys())
    st.write(f"本班学生列表：")
    if len(stu_list) == 0:
        st.info("暂无学生，请学生登录加入班级")
    else:
        row_count = (len(stu_list) + 7) // 8
        idx = 0
        for _ in range(row_count):
            cols = st.columns(8)
            for col in cols:
                if idx < len(stu_list):
                    name = stu_list[idx]
                    if name == st.session_state["random_pick_stu"]:
                        col.button(name, use_container_width=True, type="primary")
                    else:
                        col.button(name, use_container_width=True)
                    idx += 1
        st.divider()

        # ① 随机抽取1名学生 单独一行
        if st.button("随机抽取组和学生", type="primary", use_container_width=True):
            import random
            pick_name = random.choice(stu_list)
            st.session_state["random_pick_stu"] = pick_name
            # 抽取时立刻读取学生小组存入缓存
            df_stu = pd.read_csv(STUDENT_CSV, encoding="utf-8-sig")
            df_stu["group"] = df_stu["group"].fillna("").astype(str)
            target_row = df_stu[(df_stu["class_name"] == selected_class) & (df_stu["student_name"] == pick_name)]
            pick_group = ""
            if len(target_row) > 0:
                group_val = target_row.iloc[0]["group"]
                if group_val not in ["", "nan"]:
                    if group_val.endswith(".0"):
                        group_val = group_val[:-2]
                    pick_group = group_val
            st.session_state["pick_group"] = pick_group
            st.rerun()

        # ② 增亮显示被抽组和学生
        if st.session_state["random_pick_stu"] != "":
            picked_name = st.session_state["random_pick_stu"]
            df_stu = pd.read_csv(STUDENT_CSV, encoding="utf-8-sig")
            df_stu["group"] = df_stu["group"].fillna("").astype(str)
            target_row = df_stu[(df_stu["class_name"] == selected_class) & (df_stu["student_name"] == picked_name)]
            group_text = ""
            pick_group = ""
            if len(target_row) > 0:
                group_val = target_row.iloc[0]["group"]
                if group_val not in ["", "nan"]:
                    if group_val.endswith(".0"):
                        group_val = group_val[:-2]
                    group_text = f"第{group_val}组--"
                    pick_group = group_val
            show_text = f"本次抽中组和学生：{group_text}{picked_name}"
            st.markdown(f"""
            <div style="background:#165DFF;color:#fff;padding:20px;border-radius:12px;text-align:center;margin:15px 0;">
            <h2>{show_text}</h2>
            </div>
            """, unsafe_allow_html=True)

        # ③单人加分、④小组下拉、⑤整组加分、⑥清空 四栏并排
        col_c1, col_c2, col_c3, col_c4 = st.columns([2,2,2,2])
        with col_c1:
            picked = st.session_state["random_pick_stu"]
            if picked != "":
                if st.button(f"为【{picked}】+1课堂分", use_container_width=True):
                    flag, tip = add_class_point(selected_class, picked)
                    st.success(tip)
                    st.rerun()
            else:
                st.button("为选中学生+1课堂分", disabled=True, use_container_width=True)
        with col_c2:
            default_group = st.session_state.get("pick_group", "")
            select_index = 0
            if default_group in group_list:
                select_index = group_list.index(default_group)
            sel_group = st.selectbox("选择小组批量加分", group_list, index=select_index)
        with col_c3:
            if len(group_list) > 0:
                if st.button("整组全员+1分", use_container_width=True):
                    flag, tip = add_group_all_point(selected_class, sel_group)
                    st.success(tip)
                    st.rerun()
            else:
                st.button("整组全员+1分", disabled=True, use_container_width=True)
        with col_c4:
            if st.button("清空抽取结果", use_container_width=True):
                st.session_state["random_pick_stu"] = ""
                st.session_state["pick_group"] = ""
                st.rerun()

        st.divider()
        # ⑦ 给学生分配小组（移到最下方）
        st.subheader("给学生分配小组")
        c1, c2 = st.columns(2)
        sel_student = c1.selectbox("选择学生", stu_list)
        group_input = c2.text_input("小组编号（1/2/3...）", value="1")
        if st.button("保存小组设置"):
            flag, tip = set_student_group(selected_class, sel_student, group_input.strip())
            if flag:
                st.success(tip)
                st.rerun()
            else:
                st.error(tip)
        st.divider()

        # 个人积分排行榜
        st.subheader("三、学生个人积分排行榜（总分降序）")
        point_df = get_class_point(selected_class)
        if point_df.empty:
            st.info("暂无积分记录，加分后自动生成")
        else:
            point_df = point_df.sort_values("total_point", ascending=False, ignore_index=True)
            st.dataframe(point_df, use_container_width=True)
        st.divider()
        # 小组积分柱状图
        st.subheader("四、小组积分统计图表")
        group_stat = get_group_point_stat(selected_class)
        if group_stat.empty:
            st.info("请先给学生分配小组后查看统计")
        else:
            chart1, chart2 = st.columns(2)
            with chart1:
                st.subheader("各组总积分")
                st.bar_chart(group_stat, x="小组", y="小组总积分", height=320, use_container_width=True)
            with chart2:
                st.subheader("各组人均积分")
                st.bar_chart(group_stat, x="小组", y="人均积分", height=320, use_container_width=True)
            st.dataframe(group_stat, use_container_width=True)

# 班级试卷成绩分析
st.divider()
st.subheader("五、班级试卷成绩分析")
test_map = {"test1": "测试一", "test2": "测试二"}
select_test = st.selectbox("选择试卷", list(test_map.keys()), format_func=lambda x: test_map[x])
q_list = get_question_list(select_test)
if not selected_class:
    st.info("请先选择上方班级")
elif len(q_list) == 0:
    st.warning("题库question_bank.csv暂无题目")
else:
    st.write(f"班级：{selected_class} | 试卷：{test_map[select_test]}")
    btn1, btn2 = st.columns(2)
    with btn1:
        show_stat = st.button("加载班级统计分析", type="primary")
    with btn2:
        show_detail = st.button("加载全部成绩明细")
    df_score = pd.DataFrame()
    if os.path.exists(SCORE_CSV):
        df_score = pd.read_csv(SCORE_CSV, encoding=ENCODING)
    class_score = pd.DataFrame()
    if not df_score.empty and "test_id" in df_score.columns:
        class_score = df_score[(df_score["class_name"] == selected_class) & (df_score["test_id"] == select_test)].copy()
    if show_detail:
        st.divider()
        st.subheader("本班试卷成绩明细")
        if class_score.empty:
            st.warning("暂无学生提交该试卷")
        else:
            st.dataframe(class_score, use_container_width=True)
    if show_stat:
        if class_score.empty:
            st.warning("暂无提交数据")
        else:
            total_num = len(class_score)
            avg = round(class_score["total_score"].mean(), 2)
            max_s = class_score["total_score"].max()
            min_s = class_score["total_score"].min()
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("参与人数", total_num)
            with m2: st.metric("平均分", avg)
            with m3: st.metric("最高分", max_s)
            with m4: st.metric("最低分", min_s)
            st.subheader("成绩等级分布")
            st.dataframe(class_score["level"].value_counts(), use_container_width=True)
            st.divider()
            st.subheader("逐题作答分析")
            for q in q_list:
                qid = q["id"]
                score_col = f"q{qid}"
                ans_col = f"user_ans_{qid}"
                st.markdown(f"### 第{qid}题（满分{q['score']}分）")
                st.write(f"题干：{q['title']}")
                st.write(f"选项：{' | '.join(q['opts'])}")
                std_ans_txt = "、".join(q["ans"]) if isinstance(q["ans"], list) else q["ans"]
                st.write(f"标准答案：{std_ans_txt}")
                q_avg_score = round(class_score[score_col].mean(), 2)
                right_cnt = len(class_score[class_score[score_col] == q["score"]])
                wrong_cnt = total_num - right_cnt
                acc_rate = round(right_cnt / total_num * 100, 2)
                st.write(f"本题平均分：{q_avg_score} | 答对{right_cnt}/{total_num} | 正确率{acc_rate}%")
                if q["type"] == "single":
                    opt_count = {"A":0,"B":0,"C":0,"D":0}
                    if ans_col in class_score.columns:
                        for a in class_score[ans_col].dropna():
                            if a in opt_count:
                                opt_count[a] += 1
                    bar_df = pd.DataFrame({"选项":list(opt_count.keys()),"作答人数":list(opt_count.values())})
                    st.bar_chart(bar_df, x="选项", y="作答人数", height=240)
                else:
                    bar_df = pd.DataFrame({"结果":["答对","答错"],"人数":[right_cnt,wrong_cnt]})
                    st.bar_chart(bar_df, x="结果", y="人数", height=240)
                st.divider()

st.divider()
st.page_link("pages/00_教师入口首页.py", label="← 教师入口首页", use_container_width=True)