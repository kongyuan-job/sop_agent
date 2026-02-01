import streamlit as st
import requests
import json

BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Indicator AI Agent System", layout="wide")
st.title("📊 Indicator AI Agent System")

tabs = st.tabs(["问数 (Chat)", "数据源配置", "指标语义定义", "Agent 创建", "SOP 配置"])

# --- Tab 1: Chat ---
with tabs[0]:
    st.header("💬 指标问数")
    agents = requests.get(f"{BASE_URL}/agents/").json()
    if agents:
        agent_names = [a["name"] for a in agents]
        selected_agent_name = st.selectbox("选择 Agent", agent_names)
        selected_agent = next(a for a in agents if a["name"] == selected_agent_name)
        
        user_query = st.text_input("输入你的问题 (例如: 查询销售额在2023-10的数据)")
        if st.button("发送"):
            with st.spinner("Agent 正在思考..."):
                resp = requests.post(f"{BASE_URL}/query/", params={"query": user_query, "agent_id": selected_agent["id"]}).json()
                st.markdown("### 结果")
                st.write(resp["result"])
                with st.expander("执行过程"):
                    for msg in resp["history"]:
                        st.text(msg)
    else:
        st.warning("请先在 'Agent 创建' 选项卡中创建一个 Agent。")

# --- Tab 2: Data Source ---
with tabs[1]:
    st.header("🔗 数据源配置")
    with st.form("ds_form"):
        name = st.text_input("数据源名称")
        db_type = st.selectbox("数据库类型", ["sqlite", "postgresql", "mysql"])
        host = st.text_input("主机地址 / SQLite 路径")
        port = st.number_input("端口", value=5432)
        database = st.text_input("数据库名")
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        
        if st.form_submit_button("保存数据源"):
            data = {
                "name": name, "db_type": db_type, "host": host, "port": port,
                "database": database, "username": username, "password": password
            }
            resp = requests.post(f"{BASE_URL}/data_sources/", json=data)
            if resp.status_code == 200:
                st.success("数据源保存成功！")
            else:
                st.error(f"保存失败: {resp.text}")

# --- Tab 3: Indicator ---
with tabs[2]:
    st.header("📏 指标语义定义")
    data_sources = requests.get(f"{BASE_URL}/data_sources/").json()
    if data_sources:
        ds_map = {ds["name"]: ds["id"] for ds in data_sources}
        selected_ds = st.selectbox("选择数据源", list(ds_map.keys()))
        
        with st.form("indicator_form"):
            ind_name = st.text_input("指标名称")
            synonyms = st.text_input("同义词 (逗号分隔)")
            unit = st.text_input("计量单位")
            eval_crit = st.text_area("评估标准")
            formula = st.text_input("计算公式")
            table_name = st.text_input("数据库表名")
            
            st.subheader("字段信息")
            col1, col2, col3 = st.columns(3)
            f_name = col1.text_input("度量字段名")
            f_type = col2.text_input("字段类型", value="FLOAT")
            f_desc = col3.text_input("字段描述")
            
            time_name = col1.text_input("时间维度字段名")
            time_fmt = col2.text_input("时间格式", value="yyyy-MM")
            
            if st.form_submit_button("保存指标"):
                fields = [
                    {"name": f_name, "data_type": f_type, "description": f_desc, "field_role": "MEASURE"},
                    {"name": time_name, "data_type": "STRING", "description": "时间维度", "field_role": "TIME", "time_format": time_fmt}
                ]
                data = {
                    "name": ind_name, "synonyms": synonyms, "unit": unit,
                    "evaluation_criteria": eval_crit, "formula": formula,
                    "table_name": table_name, "data_source_id": ds_map[selected_ds],
                    "fields": fields
                }
                resp = requests.post(f"{BASE_URL}/indicators/", json=data)
                if resp.status_code == 200:
                    st.success("指标保存成功！")
                else:
                    st.error(f"保存失败: {resp.text}")
    else:
        st.warning("请先配置数据源。")

# --- Tab 4: Agent Create ---
with tabs[3]:
    st.header("🤖 Agent 创建")
    indicators = requests.get(f"{BASE_URL}/indicators/").json()
    with st.form("agent_form"):
        a_name = st.text_input("Agent 名称")
        a_desc = st.text_area("Agent 描述")
        selected_inds = st.multiselect("选择可用指标", [i["name"] for i in indicators])
        
        if st.form_submit_button("创建 Agent"):
            ind_ids = [i["id"] for i in indicators if i["name"] in selected_inds]
            data = {"name": a_name, "description": a_desc, "indicator_ids": ind_ids}
            resp = requests.post(f"{BASE_URL}/agents/", json=data)
            if resp.status_code == 200:
                st.success("Agent 创建成功！")
            else:
                st.error(f"创建失败: {resp.text}")

# --- Tab 5: SOP ---
with tabs[4]:
    st.header("📋 SOP 配置")
    with st.form("sop_form"):
        s_name = st.text_input("SOP 名称")
        s_desc = st.text_area("场景描述 (用于触发召回)")
        
        st.subheader("任务清单 (示例)")
        t_name = st.text_input("任务名称")
        t_detail = st.text_area("任务详情")
        
        if st.form_submit_button("保存 SOP"):
            data = {
                "name": s_name, "description": s_desc,
                "tasks": [{"name": t_name, "detail": t_detail, "tools": [], "dependencies": []}]
            }
            resp = requests.post(f"{BASE_URL}/sops/", json=data)
            if resp.status_code == 200:
                st.success("SOP 保存成功！")
            else:
                st.error(f"保存失败: {resp.text}")
