import pandas as pd
import os
import csv

# ===================== 班级配置文件 class_info.csv =====================
CLASS_CSV = "class_info.csv"
def add_class(class_name):
    if not os.path.exists(CLASS_CSV):
        df = pd.DataFrame(columns=["class_name", "code"])
        df.to_csv(CLASS_CSV, index=False, encoding="utf-8-sig")
    df = pd.read_csv(CLASS_CSV, encoding="utf-8-sig")
    if class_name in df["class_name"].values:
        return False, "班级已存在"
    import random
    code = random.randint(1000, 9999)
    new_row = pd.DataFrame([{"class_name": class_name, "code": code}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CLASS_CSV, index=False, encoding="utf-8-sig")
    return True, code

def get_all_class():
    if not os.path.exists(CLASS_CSV):
        return []
    df = pd.read_csv(CLASS_CSV, encoding="utf-8-sig")
    return df["class_name"].tolist()

def get_class_all_info():
    res = {}
    if os.path.exists(CLASS_CSV):
        df = pd.read_csv(CLASS_CSV, encoding="utf-8-sig")
        for _, row in df.iterrows():
            res[row["class_name"]] = str(row["code"])
    return res

# ===================== 学生文件 student_list.csv（彻底修复float小数点） =====================
STUDENT_CSV = "student_list.csv"
def init_student_csv():
    if not os.path.exists(STUDENT_CSV):
        df = pd.DataFrame(columns=["student_name", "class_name", "group"])
        # 新建表直接填充空字符串，杜绝NaN浮点
        df["group"] = df["group"].fillna("").astype(str)
        df.to_csv(STUDENT_CSV, index=False, encoding="utf-8-sig")
    else:
        df = pd.read_csv(STUDENT_CSV, encoding="utf-8-sig")
        # 关键：先填充空值，再强制字符串，彻底消除NaN/float
        df["group"] = df["group"].fillna("").astype(str)
        df.to_csv(STUDENT_CSV, index=False, encoding="utf-8-sig")

def add_student(class_name, stu_name):
    init_student_csv()
    df = pd.read_csv(STUDENT_CSV, encoding="utf-8-sig")
    df["group"] = df["group"].fillna("").astype(str)
    mask = (df["class_name"] == class_name) & (df["student_name"] == stu_name)
    if mask.any():
        return False, "该学生已存在"
    new_line = pd.DataFrame([{
        "student_name": stu_name,
        "class_name": class_name,
        "group": ""
    }])
    new_line["group"] = new_line["group"].fillna("").astype(str)
    df = pd.concat([df, new_line], ignore_index=True)
    df.to_csv(STUDENT_CSV, index=False, encoding="utf-8-sig")
    return True, "添加成功"

def set_student_group(class_name, stu_name, group):
    init_student_csv()
    df = pd.read_csv(STUDENT_CSV, encoding="utf-8-sig")
    df["group"] = df["group"].fillna("").astype(str)
    mask = (df["class_name"] == class_name) & (df["student_name"] == stu_name)
    if mask.any():
        idx = df[mask].index[0]
        # 写入前清洗，去除.0浮点后缀
        clean_group = str(group).strip()
        if clean_group.endswith(".0"):
            clean_group = clean_group[:-2]
        df.loc[idx, "group"] = clean_group
        df.to_csv(STUDENT_CSV, index=False, encoding="utf-8-sig")
        return True, "组别分配完成"
    return False, "未找到该学生"

def get_students_by_class(class_name):
    init_student_csv()
    df = pd.read_csv(STUDENT_CSV, encoding="utf-8-sig")
    df["group"] = df["group"].fillna("").astype(str)
    target = df[df["class_name"] == class_name]
    return target["student_name"].tolist()

def get_class_group_map(class_name):
    init_student_csv()
    df = pd.read_csv(STUDENT_CSV, encoding="utf-8-sig")
    df["group"] = df["group"].fillna("").astype(str)
    df_cls = df[df["class_name"] == class_name]
    group_dict = {}
    for _, row in df_cls.iterrows():
        g = row["group"]
        # 过滤空值和nan
        if g == "" or g == "nan":
            continue
        # 清洗浮点后缀
        if g.endswith(".0"):
            g = g[:-2]
        if g not in group_dict:
            group_dict[g] = []
        group_dict[g].append(row["student_name"])
    return group_dict

# ===================== 积分表 student_score.csv =====================
POINT_CSV = "student_score.csv"
def init_point_csv():
    if not os.path.exists(POINT_CSV):
        df = pd.DataFrame(columns=["class_name", "student_name", "test1_add", "test2_add", "class_point", "total_point"])
        df.to_csv(POINT_CSV, index=False, encoding="utf-8-sig")

def add_class_point(class_name, stu_name):
    init_point_csv()
    df = pd.read_csv(POINT_CSV, encoding="utf-8-sig")
    mask = (df["class_name"] == class_name) & (df["student_name"] == stu_name)
    if mask.any():
        idx = df[mask].index[0]
        df.loc[idx, "class_point"] += 1
        t1 = df.loc[idx, "test1_add"] * 3
        t2 = df.loc[idx, "test2_add"] * 2
        df.loc[idx, "total_point"] = df.loc[idx, "class_point"] + t1 + t2
    else:
        new_row = {
            "class_name": class_name,
            "student_name": stu_name,
            "test1_add": 0,
            "test2_add": 0,
            "class_point": 1,
            "total_point": 1
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(POINT_CSV, index=False, encoding="utf-8-sig")
    return True, "加分成功"

def add_group_all_point(class_name, group_name):
    group_map = get_class_group_map(class_name)
    if group_name not in group_map:
        return False, "该小组暂无学生"
    stu_list = group_map[group_name]
    count = 0
    for s in stu_list:
        add_class_point(class_name, s)
        count += 1
    return True, f"{group_name}小组共{count}名学生全部+1课堂积分"

def auto_test_point(class_name, stu_name, test_id, level):
    init_point_csv()
    df = pd.read_csv(POINT_CSV, encoding="utf-8-sig")
    target_col = "test1_add" if test_id == "test1" else "test2_add"
    level_score = {"优秀": 3, "良好": 2, "及格": 1, "不及格": 0}
    add_score = level_score[level]
    mask = (df["class_name"] == class_name) & (df["student_name"] == stu_name)
    if mask.any():
        idx = df[mask].index[0]
        if df.loc[idx, target_col] == 1:
            return False, "该试卷积分已发放，不可重复加分"
        df.loc[idx, target_col] = 1
        df.loc[idx, "total_point"] += add_score
    else:
        t1_flag = 1 if test_id == "test1" else 0
        t2_flag = 1 if test_id == "test2" else 0
        new_row = {
            "class_name": class_name,
            "student_name": stu_name,
            "test1_add": t1_flag,
            "test2_add": t2_flag,
            "class_point": 0,
            "total_point": add_score
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(POINT_CSV, index=False, encoding="utf-8-sig")
    return True, f"自动发放{add_score}分"

def get_class_point(class_name):
    init_point_csv()
    df = pd.read_csv(POINT_CSV, encoding="utf-8-sig")
    return df[df["class_name"] == class_name].copy()

def get_group_point_stat(class_name):
    df_stu = pd.read_csv(STUDENT_CSV, encoding="utf-8-sig")
    df_stu["group"] = df_stu["group"].fillna("").astype(str)
    df_stu = df_stu[df_stu["class_name"] == class_name]
    df_point = get_class_point(class_name)
    merge_df = pd.merge(df_stu, df_point, left_on=["class_name", "student_name"], right_on=["class_name", "student_name"], how="left")
    merge_df["total_point"] = merge_df["total_point"].fillna(0)
    sum_group = merge_df.groupby("group")["total_point"].sum().reset_index()
    avg_group = merge_df.groupby("group")["total_point"].mean().round(2).reset_index()
    count_group = merge_df.groupby("group").size().reset_index(name="小组人数")
    stat_df = pd.merge(sum_group, avg_group, on="group")
    stat_df = pd.merge(stat_df, count_group, on="group")
    # 清洗分组名称，去除.0
    stat_df["group"] = stat_df["group"].apply(lambda x: x[:-2] if x.endswith(".0") else x)
    stat_df.columns = ["小组", "小组总积分", "人均积分", "小组人数"]
    return stat_df

# ===================== 题库读取 question_bank.csv =====================
def get_question_list(test_id):
    res = []
    if not os.path.exists("question_bank.csv"):
        return res
    with open("question_bank.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["test_id"] == test_id:
                ans = row["ans"].split(",") if "," in row["ans"] else row["ans"]
                opts = row["opts"].split("|")
                item = {
                    "id": row["id"],
                    "type": row["type"],
                    "score": int(row["score"]),
                    "title": row["title"],
                    "opts": opts,
                    "ans": ans,
                    "analysis": row["analysis"]
                }
                res.append(item)
    return res