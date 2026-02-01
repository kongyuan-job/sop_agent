from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import init_db, get_db
from .schemas import schemas
from .services import metadata_service
from .agents.indicator_agent import app_graph
from langchain_core.messages import HumanMessage
import uvicorn

app = FastAPI(title="Indicator AI Agent System")

@app.on_event("startup")
def startup():
    init_db()

# Data Source Endpoints
@app.post("/data_sources/", response_model=schemas.DataSource)
def create_data_source(ds: schemas.DataSourceCreate, db: Session = Depends(get_db)):
    return metadata_service.create_data_source(db, ds)

@app.get("/data_sources/", response_model=list[schemas.DataSource])
def get_data_sources(db: Session = Depends(get_db)):
    return metadata_service.get_data_sources(db)

@app.post("/data_sources/test")
def test_connection(ds: schemas.DataSourceBase):
    success, msg = metadata_service.test_connection(ds)
    return {"success": success, "message": msg}

# Indicator Endpoints
@app.post("/indicators/", response_model=schemas.Indicator)
def create_indicator(indicator: schemas.IndicatorCreate, db: Session = Depends(get_db)):
    return metadata_service.create_indicator(db, indicator)

@app.get("/indicators/", response_model=list[schemas.Indicator])
def get_indicators(db: Session = Depends(get_db)):
    return metadata_service.get_indicators(db)

# Agent Endpoints
@app.post("/agents/", response_model=schemas.Agent)
def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    return metadata_service.create_agent(db, agent)

@app.get("/agents/", response_model=list[schemas.Agent])
def get_agents(db: Session = Depends(get_db)):
    return metadata_service.get_agents(db)

# SOP Endpoints
@app.post("/sops/", response_model=schemas.SOP)
def create_sop(sop: schemas.SOPCreate, db: Session = Depends(get_db)):
    return metadata_service.create_sop(db, sop)

@app.get("/sops/", response_model=list[schemas.SOP])
def get_sops(db: Session = Depends(get_db)):
    return metadata_service.get_sops(db)

# Chat/Query Endpoint
@app.post("/query/")
async def query_agent(query: str, agent_id: int):
    # In a real app, we'd load the agent configuration by agent_id
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "indicators": [],
        "sop_id": None,
        "current_task_index": 0,
        "report": ""
    }
    
    final_state = await app_graph.ainvoke(initial_state)
    
    # Return the last message content as the result
    return {
        "result": final_state["messages"][-1].content,
        "history": [m.content for m in final_state["messages"]]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
