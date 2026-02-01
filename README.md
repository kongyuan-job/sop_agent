# 指标问数 AI Agent 系统

这是一个基于 Python 的 AI Agent 系统，旨在帮助用户通过自然语言提问来查询业务指标数据。系统集成了指标语义管理、SOP（标准作业程序）配置以及基于 LangGraph 的智能编排能力。

## 🚀 核心功能

1.  **指标语义构建**：支持配置数据库数据源，定义指标基础信息（同义词、单位、公式）及字段信息（度量、时间维度、普通维度）。
2.  **通用指标工具**：提供查询指标语义和查询指标值的 Tool，支持同比、环比计算。
3.  **Agent 编排**：基于 LangGraph 实现，具备指标识别、SOP 召回、通用问数和 SOP 执行等多种模式。
4.  **可视化管理后台**：使用 Streamlit 构建，提供数据源配置、指标定义、Agent 创建及 SOP 配置的直观界面。
5.  **报告生成**：支持流式展示 Agent 执行过程，并可根据配置生成 HTML 报告。

## 📂 项目结构

```text
.
├── app/
│   ├── agents/            # LangGraph 工作流定义
│   ├── models/            # SQLAlchemy 数据库模型 (SQLite/PostgreSQL)
│   ├── schemas/           # Pydantic 数据验证模型
│   ├── services/          # 指标语义及数据处理业务层
│   ├── tools/             # LangChain 自定义工具 (语义查询、数值计算)
│   ├── db.py              # 数据库连接配置
│   └── main.py            # FastAPI 接口服务
├── ui/
│   └── app.py             # Streamlit 后台管理及问数界面
├── requirements.txt       # 项目依赖
├── .env.example           # 环境变量模板 (OpenAI API Key 等)
├── init_dummy_data.py     # 初始化模拟业务数据的脚本
└── README.md              # 项目说明文档
```

## 🛠️ 快速开始

### 1. 环境准备
确保已安装 Python 3.9+。

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
将 `.env.example` 重命名为 `.env`，并配置您的 OpenAI API Key。

```text
OPENAI_API_KEY=sk-xxxx
```

### 3. 初始化模拟数据（可选）
如果您没有现成的数据库，可以运行此脚本生成一个包含销售数据的 SQLite 数据库用于测试：

```bash
python init_dummy_data.py
```

### 4. 启动后端服务

```bash
python -m app.main
```
后端服务将运行在 `http://localhost:8000`。

### 5. 启动前端界面

```bash
streamlit run ui/app.py
```
访问浏览器显示的地址（通常是 `http://localhost:8501`）即可开始配置和问数。

## 💡 使用流程
1.  **配置数据源**：在 UI 的“数据源配置”中添加数据库连接。
2.  **定义指标**：在“指标语义定义”中绑定数据表及字段映射。
3.  **创建 Agent**：在“Agent 创建”中配置 Agent 的名称并关联可用指标。
4.  **配置 SOP（可选）**：定义特定场景下的标准查询流程。
5.  **开始问数**：在“问数 (Chat)”选项卡中与 Agent 交互，例如：“查询 2023-10 的销售额”。

## ⚖️ 技术栈
- **后端**: FastAPI, SQLAlchemy, Pydantic
- **大模型框架**: LangChain, LangGraph
- **前端**: Streamlit
- **数据处理**: Pandas
- **数据库**: SQLite (默认), 支持 PostgreSQL/MySQL
