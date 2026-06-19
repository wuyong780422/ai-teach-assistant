import pandas as pd
import random
import os
# 文件路径
CLASS_CSV = "class_data.csv"
STUDENT_CSV = "student_data.csv"
QUESTION_CSV = "question_bank.csv"
# 统一UTF-8编码，解决中文乱码
ENCODING = "utf-8-sig"

# 生成4位随机验证码
def create_verify_code():
    return str(random.randint(1000, 9999))

# ========== 班级操作 ==========
# 创建班级，不存在则新增
def add_class(class_name):
    code = create_verify_code()
    new_row = pd.DataFrame([{"class_name": class_name, "verify_code": code}])
    if os.path.exists(CLASS_CSV):
        df = pd.read_csv(CLASS_CSV, encoding=ENCODING)
        # 重复班级不创建
        if class_name in df["class_name"].tolist():
            return False, "班级已存在"
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    # 写入强制utf-8-sig，Excel打开不乱码
    df.to_csv(CLASS_CSV, index=False, encoding=ENCODING)
    return True, code

# 根据班级名查验证码
def get_class_code(class_name):
    if not os.path.exists(CLASS_CSV):
        return None
    df = pd.read_csv(CLASS_CSV, encoding=ENCODING)
    res = df[df["class_name"].str.strip() == class_name.strip()]
    if len(res) == 0:
        return None
    return str(res.iloc[0]["verify_code"]).strip()

# 获取全部班级列表
def get_all_class():
    if not os.path.exists(CLASS_CSV):
        return []
    df = pd.read_csv(CLASS_CSV, encoding=ENCODING)
    class_list = [i.strip() for i in df["class_name"].tolist()]
    return class_list

# 获取班级+验证码完整字典
def get_class_all_info():
    if not os.path.exists(CLASS_CSV):
        return {}
    df = pd.read_csv(CLASS_CSV, encoding=ENCODING)
    info_dict = {}
    for _, row in df.iterrows():
        c_name = str(row["class_name"]).strip()
        c_code = str(row["verify_code"]).strip()
        info_dict[c_name] = c_code
    return info_dict

# ========== 学生操作 ==========
# 新增学生
def add_student(student_name, class_name):
    # 校验班级是否存在
    if get_class_code(class_name) is None:
        return False, "班级不存在"
    new_row = pd.DataFrame([{"student_name": student_name, "class_name": class_name}])
    if os.path.exists(STUDENT_CSV):
        df = pd.read_csv(STUDENT_CSV, encoding=ENCODING)
        # 同班级同名学生禁止重复加入
        cond = (df["student_name"].str.strip() == student_name.strip()) & (df["class_name"].str.strip() == class_name.strip())
        if len(df[cond]) > 0:
            return False, "该学生已加入此班级"
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(STUDENT_CSV, index=False, encoding=ENCODING)
    return True, "加入成功"

# 根据班级获取该班所有学生
def get_students_by_class(class_name):
    if not os.path.exists(STUDENT_CSV):
        return []
    df = pd.read_csv(STUDENT_CSV, encoding=ENCODING)
    res = df[df["class_name"].str.strip() == class_name.strip()]
    student_list = [i.strip() for i in res["student_name"].tolist()]
    return student_list

# 校验验证码+班级是否匹配
def check_class_code(class_name, input_code):
    real_code = get_class_code(class_name)
    if real_code is None:
        return False
    # 两边去除空格再对比
    input_clean = input_code.strip()
    real_clean = real_code.strip()
    return real_clean == input_clean

# ========== 题库读取新函数（无重名，新增区块） ==========
def get_question_list(test_id="test1"):
    """根据试卷标识读取对应题库，返回题目字典列表"""
    if not os.path.exists(QUESTION_CSV):
        return []
    df = pd.read_csv(QUESTION_CSV, encoding=ENCODING)
    df_target = df[df["test_id"] == test_id].copy()
    q_list = []
    for _, row in df_target.iterrows():
        opts_arr = row["opts"].split("|")
        if row["type"] == "multi":
            ans_arr = row["ans"].split(",")
        else:
            ans_arr = row["ans"]
        q_item = {
            "id": int(row["id"]),
            "type": row["type"],
            "score": int(row["score"]),
            "title": row["title"],
            "opts": opts_arr,
            "ans": ans_arr,
            "analysis": row["analysis"]
        }
        q_list.append(q_item)
    return q_list