import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import io
from github import Github, GithubException

st.set_page_config(page_title="数学错题统计", layout="wide")
st.title("📚 数学错题归因 & 周月统计系统")

# 界面中文选项
ERROR_TYPES = ["计算失误", "审题错误", "概念不清", "解题无思路", "步骤遗漏", "抄写错误", "粗心大意"]
QUESTION_TYPES = ["选择题", "填空题", "计算题", "应用题", "其他"]

# 数据文件 纯英文，独立存放，迭代不丢数据
DATA_FILE = "wrong_questions.csv"
COLUMNS = ["date", "q_type", "question", "ans_wrong", "ans_right", "error_type", "notes"]
REPO_NAME = "zcchm/math-wrong-questions"

# --- GitHub 持久化（Streamlit Cloud 用） ---
def _get_github():
    try:
        token = st.secrets.get("GITHUB_TOKEN")
        if token:
            return Github(token)
    except Exception:
        pass
    return None

def _load_from_github():
    g = _get_github()
    if not g:
        return None
    try:
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(DATA_FILE)
        csv_str = contents.decoded_content.decode("utf-8")
        df = pd.read_csv(io.StringIO(csv_str))
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df
    except GithubException:
        return None

def _save_to_github(df):
    g = _get_github()
    if not g:
        return False
    try:
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(DATA_FILE)
        csv_str = df.to_csv(index=False, encoding="utf-8")
        repo.update_file(contents.path, "update wrong_questions.csv", csv_str, contents.sha)
        return True
    except GithubException:
        return False

# 加载数据：GitHub → 本地回退 → 初始化空表
def load_data():
    df = _load_from_github()
    if df is not None:
        return df
    try:
        df = pd.read_csv(DATA_FILE, encoding="utf-8")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    except:
        df = pd.DataFrame(columns=COLUMNS)
        save_data(df)
    return df

def save_data(df):
    if _save_to_github(df):
        return
    df.to_csv(DATA_FILE, index=False, encoding="utf-8")

# 初始化
if "df" not in st.session_state:
    st.session_state.df = load_data()

# 侧边栏 新增/编辑错题
with st.sidebar:
    st.header("✅ 错题操作")
    mode = st.radio("模式", ["添加错题", "编辑错题"])

    if mode == "添加错题":
        today = date.today()
        q_type = st.selectbox("题型", QUESTION_TYPES)
        question = st.text_input("题目简述")
        ans_wrong = st.text_input("错误答案")
        ans_right = st.text_input("正确答案")
        error_type = st.selectbox("错误原因", ERROR_TYPES)
        notes = st.text_input("备注（可选）")

        if st.button("💾 保存"):
            if question and ans_wrong and ans_right:
                new_row = pd.DataFrame([[
                    today, q_type, question, ans_wrong, ans_right, error_type, notes
                ]], columns=COLUMNS)
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.success("保存成功，历史数据完好保留！")
            else:
                st.error("题目、答案不能为空")

    elif mode == "编辑错题" and not st.session_state.df.empty:
        df = st.session_state.df
        idx = st.number_input("选择序号", 0, len(df)-1, 0)
        row = df.iloc[idx]

        edit_qtype = st.selectbox("题型", QUESTION_TYPES, index=QUESTION_TYPES.index(row["q_type"]))
        edit_question = st.text_input("题目", value=row["question"])
        edit_ans_wrong = st.text_input("错误答案", value=row["ans_wrong"])
        edit_ans_right = st.text_input("正确答案", value=row["ans_right"])
        edit_error = st.selectbox("错误原因", ERROR_TYPES, index=ERROR_TYPES.index(row["error_type"]))
        edit_notes = st.text_input("备注", value=str(row["notes"]) if pd.notna(row["notes"]) else "")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 更新"):
                st.session_state.df.loc[idx] = [
                    date.today(), edit_qtype, edit_question, edit_ans_wrong, edit_ans_right, edit_error, edit_notes
                ]
                save_data(st.session_state.df)
                st.success("已更新")
        with c2:
            if st.button("🗑️ 删除本条"):
                st.session_state.df = df.drop(idx).reset_index(drop=True)
                save_data(st.session_state.df)
                st.warning("已删除")

# 主界面：手动输入日期范围 + 周/月统计
df_all = st.session_state.df.copy()
st.divider()
st.subheader("📅 自定义时间范围查询（可手动选日期）")

if not df_all.empty:
    min_dt = df_all["date"].min().date()
    max_dt = df_all["date"].max().date()
    start_date, end_date = st.date_input("选择起止日期", [min_dt, max_dt])

    # 筛选时间段数据
    df_all["dt_date"] = df_all["date"].dt.date
    df_filter = df_all[(df_all["dt_date"] >= start_date) & (df_all["dt_date"] <= end_date)]

    tab1, tab2, tab3 = st.tabs(["📊 每日统计", "📅 每周统计", "🗓️ 每月统计"])

    with tab1:
        day_cnt = df_filter.groupby("dt_date").size().reset_index(name="错题数")
        st.bar_chart(day_cnt, x="dt_date", y="错题数")

    with tab2:
        df_filter["year_week"] = df_filter["date"].dt.strftime("%Y-W%U")
        week_cnt = df_filter.groupby("year_week").size().reset_index(name="错题数")
        st.bar_chart(week_cnt, x="year_week", y="错题数")

    with tab3:
        df_filter["year_month"] = df_filter["date"].dt.strftime("%Y-%m")
        month_cnt = df_filter.groupby("year_month").size().reset_index(name="错题数")
        st.bar_chart(month_cnt, x="year_month", y="错题数")

    st.divider()
    st.subheader("全局错题分析")
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.pie(df_all, names="error_type", title="错误类型分布")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.bar(df_all, x="q_type", title="各题型错题数量")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("全部错题记录（历史数据完整保留）")
    st.dataframe(df_all, use_container_width=True)

    st.download_button(
        "📥 导出全部历史数据备份",
        df_all.to_csv(index=False, encoding="utf-8"),
        "wrong_questions_backup.csv"
    )
else:
    st.info("暂无错题数据，请先在左侧添加错题")
