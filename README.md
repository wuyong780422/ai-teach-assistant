# ai-teach-assistant
# 中职教学智能助手-数字技术赋能民族地区中职数学有效课堂
基于 Streamlit 开发的轻量化教学管理系统，支持班级管理、在线测试、任务发布、教学资源、AI备课、PPT一键生成等功能。

## 功能模块
- 教师端：班级管理、试卷管理、任务管理、资源管理、AI备课助手、PPT一键生成
- 学生端：班级任务查看、教学资源下载、在线测试答题
- 配套：课堂积分、小组管理、成绩分析、随机抽人

## 本地运行
1. 安装依赖：`pip install -r requirements.txt`
2. 在项目根目录新建 `.streamlit/secrets.toml`，配置AI密钥：
   ```toml
   DEEPSEEK_API_KEY = "你的密钥"
   # 或 DASHSCOPE_API_KEY = "你的密钥"
