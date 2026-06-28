import pandas as pd
import os
import csv
import datetime

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

# ===================== 学生文件 student_list.csv =====================
STUDENT_CSV = "student_list.csv"

def init_student_csv():
    if not os.path.exists(STUDENT_CSV):
        df = pd.DataFrame(columns=["student_name", "class_name", "group"])
        df["group"] = df["group"].fillna("").astype(str)
        df.to_csv(STUDENT_CSV, index=False, encoding="utf-8-sig")
    else:
        df = pd.read_csv(STUDENT_CSV, encoding="utf-8-sig")
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
        idx = mask.idxmax()
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
        if g == "" or g == "nan":
            continue
        if g.endswith(".0"):
            g = g[:-2]
        if g not in group_dict:
            group_dict[g] = []
        group_dict[g].append(row["student_name"])
    return group_dict

# ===================== 课堂积分表 student_score.csv =====================
POINT_CSV = "student_score.csv"

def init_point_csv():
    if not os.path.exists(POINT_CSV):
        df = pd.DataFrame(columns=["class_name", "student_name", "class_point"])
        df.to_csv(POINT_CSV, index=False, encoding="utf-8-sig")

def add_class_point(class_name, stu_name):
    init_point_csv()
    df = pd.read_csv(POINT_CSV, encoding="utf-8-sig")
    mask = (df["class_name"] == class_name) & (df["student_name"] == stu_name)
    if mask.any():
        idx = mask.idxmax()
        df.loc[idx, "class_point"] += 1
    else:
        new_row = {
            "class_name": class_name,
            "student_name": stu_name,
            "class_point": 1
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
                opts = row["opts"].split("|") if row["opts"] else []
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

# ===================== 试卷主表 paper_info.csv =====================
PAPER_CSV = "paper_info.csv"

def init_paper_csv():
    if not os.path.exists(PAPER_CSV):
        df = pd.DataFrame(columns=["paper_id", "paper_name", "total_score", "question_count", "assign_class", "create_time"])
        df.to_csv(PAPER_CSV, index=False, encoding="utf-8-sig")

def add_new_paper(paper_name, question_count, assign_class_list):
    init_paper_csv()
    df = pd.read_csv(PAPER_CSV, encoding="utf-8-sig")
    max_num = 0
    for pid in df["paper_id"].values:
        if str(pid).startswith("paper_"):
            try:
                num = int(str(pid).split("_")[1])
                if num > max_num:
                    max_num = num
            except:
                pass
    new_paper_id = f"paper_{str(max_num + 1).zfill(3)}"
    assign_str = ",".join(assign_class_list)
    new_row = {
        "paper_id": new_paper_id,
        "paper_name": paper_name.strip(),
        "total_score": 100,
        "question_count": int(question_count),
        "assign_class": assign_str,
        "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(PAPER_CSV, index=False, encoding="utf-8-sig")
    return new_paper_id

def get_all_papers():
    init_paper_csv()
    df = pd.read_csv(PAPER_CSV, encoding="utf-8-sig")
    return df.to_dict("records")

def get_class_papers(class_name):
    init_paper_csv()
    df = pd.read_csv(PAPER_CSV, encoding="utf-8-sig")
    paper_list = []
    for _, row in df.iterrows():
        assign = str(row["assign_class"])
        if assign == "all" or class_name in assign.split(","):
            paper_list.append({
                "paper_id": row["paper_id"],
                "paper_name": row["paper_name"],
                "total_score": row["total_score"],
                "question_count": row["question_count"]
            })
    return paper_list

# ===================== 题库写入函数 =====================
def add_question(paper_id, q_id, q_type, score, title, opt_a="", opt_b="", opt_c="", opt_d="", ans="", analysis=""):
    opts_str = ""
    if q_type in ["single", "multi"]:
        opts_list = [f"A.{opt_a.strip()}", f"B.{opt_b.strip()}", f"C.{opt_c.strip()}", f"D.{opt_d.strip()}"]
        opts_str = "|".join(opts_list)
    if isinstance(ans, list):
        ans_str = ",".join(ans)
    else:
        ans_str = ans
    new_row = {
        "test_id": paper_id,
        "id": str(q_id),
        "type": q_type,
        "score": int(score),
        "title": title.strip(),
        "opts": opts_str,
        "ans": ans_str,
        "analysis": analysis.strip()
    }
    if os.path.exists("question_bank.csv"):
        df = pd.read_csv("question_bank.csv", encoding="utf-8-sig")
    else:
        df = pd.DataFrame(columns=["test_id", "id", "type", "score", "title", "opts", "ans", "analysis"])
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv("question_bank.csv", index=False, encoding="utf-8-sig")
    return True

# ===================== 通用试卷积分表 paper_score.csv =====================
PAPER_SCORE_CSV = "paper_score.csv"

def init_paper_score_csv():
    if not os.path.exists(PAPER_SCORE_CSV):
        df = pd.DataFrame(columns=["class_name", "student_name", "paper_id", "point", "add_time"])
        df.to_csv(PAPER_SCORE_CSV, index=False, encoding="utf-8-sig")

def auto_paper_point(class_name, stu_name, paper_id, level):
    init_paper_score_csv()
    df = pd.read_csv(PAPER_SCORE_CSV, encoding="utf-8-sig")
    mask = (df["class_name"] == class_name) & (df["student_name"] == stu_name) & (df["paper_id"] == paper_id)
    if mask.any():
        return False, "该试卷积分已发放，不可重复加分"
    level_score = {"优秀": 3, "良好": 2, "及格": 1, "不及格": 0}
    add_score = level_score[level]
    new_row = {
        "class_name": class_name,
        "student_name": stu_name,
        "paper_id": paper_id,
        "point": add_score,
        "add_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(PAPER_SCORE_CSV, index=False, encoding="utf-8-sig")
    return True, f"自动发放{add_score}分"

def is_paper_finished(name, cls, paper_id):
    SCORE_CSV = "score_data.csv"
    if not os.path.exists(SCORE_CSV):
        return False
    df = pd.read_csv(SCORE_CSV, encoding="utf-8-sig")
    if "test_id" not in df.columns:
        return False
    df["student_name"] = df["student_name"].astype(str).str.strip()
    df["class_name"] = df["class_name"].astype(str).str.strip()
    target_name = name.strip()
    target_cls = cls.strip()
    match = df[(df["student_name"] == target_name) & (df["class_name"] == target_cls) & (df["test_id"] == paper_id)]
    return len(match) > 0

# ===================== 积分统计与排行榜 =====================
def get_class_point(class_name):
    init_point_csv()
    init_paper_score_csv()
    df_class = pd.read_csv(POINT_CSV, encoding="utf-8-sig")
    df_class = df_class[df_class["class_name"] == class_name].copy()
    df_paper = pd.read_csv(PAPER_SCORE_CSV, encoding="utf-8-sig")
    df_paper = df_paper[df_paper["class_name"] == class_name].copy()
    all_students = set()
    if not df_class.empty:
        all_students.update(df_class["student_name"].tolist())
    if not df_paper.empty:
        df_paper_sum = df_paper.groupby("student_name")["point"].sum().reset_index()
        df_paper_sum.columns = ["student_name", "paper_point"]
        all_students.update(df_paper_sum["student_name"].tolist())
    else:
        df_paper_sum = pd.DataFrame(columns=["student_name", "paper_point"])
    df_total = pd.DataFrame({"student_name": list(all_students)})
    df_total["class_name"] = class_name
    if not df_class.empty:
        df_total = pd.merge(df_total, df_class[["student_name", "class_point"]], on="student_name", how="left")
    else:
        df_total["class_point"] = 0
    df_total["class_point"] = df_total["class_point"].fillna(0).astype(int)
    if not df_paper_sum.empty:
        df_total = pd.merge(df_total, df_paper_sum, on="student_name", how="left")
    else:
        df_total["paper_point"] = 0
    df_total["paper_point"] = df_total["paper_point"].fillna(0).astype(int)
    df_total["total_point"] = df_total["class_point"] + df_total["paper_point"]
    return df_total

def get_group_point_stat(class_name):
    df_stu = pd.read_csv(STUDENT_CSV, encoding="utf-8-sig")
    df_stu["group"] = df_stu["group"].fillna("").astype(str)
    df_stu = df_stu[df_stu["class_name"] == class_name]
    df_point = get_class_point(class_name)
    merge_df = pd.merge(df_stu, df_point, left_on=["class_name", "student_name"],
                        right_on=["class_name", "student_name"], how="left")
    merge_df["total_point"] = merge_df["total_point"].fillna(0)
    sum_group = merge_df.groupby("group")["total_point"].sum().reset_index()
    avg_group = merge_df.groupby("group")["total_point"].mean().round(2).reset_index()
    count_group = merge_df.groupby("group").size().reset_index(name="小组人数")
    stat_df = pd.merge(sum_group, avg_group, on="group")
    stat_df = pd.merge(stat_df, count_group, on="group")
    stat_df["group"] = stat_df["group"].apply(lambda x: x[:-2] if x.endswith(".0") else x)
    stat_df.columns = ["小组", "小组总积分", "人均积分", "小组人数"]
    return stat_df

# ===================== 任务管理模块 =====================
TASK_CSV = "task_info.csv"
TASK_FILE_DIR = "task_files"

def init_task_csv():
    if not os.path.exists(TASK_FILE_DIR):
        os.makedirs(TASK_FILE_DIR)
    if not os.path.exists(TASK_CSV):
        df = pd.DataFrame(columns=[
            "task_id", "task_title", "task_content",
            "file_name", "assign_class", "deadline", "create_time"
        ])
        df.to_csv(TASK_CSV, index=False, encoding="utf-8-sig")

def add_task(title, content, file_names, assign_class_list, deadline=""):
    init_task_csv()
    df = pd.read_csv(TASK_CSV, encoding="utf-8-sig")
    max_id = 0
    if len(df) > 0:
        id_list = df["task_id"].apply(lambda x: int(x.replace("task_", ""))).tolist()
        max_id = max(id_list)
    new_id = f"task_{str(max_id + 1).zfill(3)}"
    assign_str = ",".join(assign_class_list)
    file_str = ",".join(file_names) if file_names else ""
    new_row = {
        "task_id": new_id,
        "task_title": title,
        "task_content": content,
        "file_name": file_str,
        "assign_class": assign_str,
        "deadline": deadline,
        "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(TASK_CSV, index=False, encoding="utf-8-sig")
    return new_id

def get_all_tasks():
    init_task_csv()
    df = pd.read_csv(TASK_CSV, encoding="utf-8-sig")
    return df.to_dict("records")

def get_class_tasks(class_name):
    init_task_csv()
    df = pd.read_csv(TASK_CSV, encoding="utf-8-sig")
    if len(df) == 0:
        return []
    mask = df["assign_class"].apply(lambda x: class_name in str(x).split(","))
    return df[mask].to_dict("records")

def update_task_assign(task_id, new_class_list):
    init_task_csv()
    df = pd.read_csv(TASK_CSV, encoding="utf-8-sig")
    assign_str = ",".join(new_class_list)
    df.loc[df["task_id"] == task_id, "assign_class"] = assign_str
    df.to_csv(TASK_CSV, index=False, encoding="utf-8-sig")
    return True

def delete_task(task_id):
    init_task_csv()
    df = pd.read_csv(TASK_CSV, encoding="utf-8-sig")
    target = df[df["task_id"] == task_id]
    if len(target) > 0:
        file_str = target.iloc[0]["file_name"]
        if pd.notna(file_str) and str(file_str).strip() != "":
            for f in str(file_str).split(","):
                file_path = os.path.join(TASK_FILE_DIR, f)
                if os.path.exists(file_path):
                    os.remove(file_path)
    df = df[df["task_id"] != task_id]
    df.to_csv(TASK_CSV, index=False, encoding="utf-8-sig")
    return True

# ===================== 资源管理模块 =====================
RESOURCE_CSV = "resource_info.csv"
RESOURCE_FILE_DIR = "resource_files"

def init_resource_csv():
    if not os.path.exists(RESOURCE_FILE_DIR):
        os.makedirs(RESOURCE_FILE_DIR)
    if not os.path.exists(RESOURCE_CSV):
        df = pd.DataFrame(columns=[
            "res_id", "res_name", "res_type", "file_name",
            "assign_class", "create_time"
        ])
        df.to_csv(RESOURCE_CSV, index=False, encoding="utf-8-sig")

def add_resource(res_name, res_type, file_name, assign_class_list):
    init_resource_csv()
    df = pd.read_csv(RESOURCE_CSV, encoding="utf-8-sig")
    max_id = 0
    if len(df) > 0:
        id_list = df["res_id"].apply(lambda x: int(x.replace("res_", ""))).tolist()
        max_id = max(id_list)
    new_id = f"res_{str(max_id + 1).zfill(3)}"
    assign_str = ",".join(assign_class_list)
    new_row = {
        "res_id": new_id,
        "res_name": res_name,
        "res_type": res_type,
        "file_name": file_name,
        "assign_class": assign_str,
        "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(RESOURCE_CSV, index=False, encoding="utf-8-sig")
    return new_id

def get_all_resources():
    init_resource_csv()
    df = pd.read_csv(RESOURCE_CSV, encoding="utf-8-sig")
    return df.to_dict("records")

def get_class_resources(class_name):
    init_resource_csv()
    df = pd.read_csv(RESOURCE_CSV, encoding="utf-8-sig")
    if len(df) == 0:
        return []
    mask = df["assign_class"].apply(lambda x: class_name in str(x).split(","))
    return df[mask].to_dict("records")

def update_resource_assign(res_id, new_class_list):
    init_resource_csv()
    df = pd.read_csv(RESOURCE_CSV, encoding="utf-8-sig")
    assign_str = ",".join(new_class_list)
    df.loc[df["res_id"] == res_id, "assign_class"] = assign_str
    df.to_csv(RESOURCE_CSV, index=False, encoding="utf-8-sig")
    return True

def delete_resource(res_id):
    init_resource_csv()
    df = pd.read_csv(RESOURCE_CSV, encoding="utf-8-sig")
    target = df[df["res_id"] == res_id]
    if len(target) > 0:
        file_str = target.iloc[0]["file_name"]
        if pd.notna(file_str) and str(file_str).strip() != "":
            file_path = os.path.join(RESOURCE_FILE_DIR, str(file_str))
            if os.path.exists(file_path):
                os.remove(file_path)
    df = df[df["res_id"] != res_id]
    df.to_csv(RESOURCE_CSV, index=False, encoding="utf-8-sig")
    return True