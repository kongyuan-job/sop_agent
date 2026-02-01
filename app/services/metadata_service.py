from sqlalchemy.orm import Session
from ..models import database as models
from ..schemas import schemas
from sqlalchemy import create_engine
import pandas as pd

def test_connection(ds: schemas.DataSourceBase):
    if ds.db_type == "sqlite":
        # For sqlite, host is the file path
        url = f"sqlite:///{ds.host}"
    else:
        url = f"{ds.db_type}://{ds.username}:{ds.password}@{ds.host}:{ds.port}/{ds.database}"
    
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            return True, "Connection successful"
    except Exception as e:
        return False, str(e)

# DataSource CRUD
def create_data_source(db: Session, ds: schemas.DataSourceCreate):
    db_ds = models.DataSource(**ds.dict())
    db.add(db_ds)
    db.commit()
    db.refresh(db_ds)
    return db_ds

def get_data_sources(db: Session):
    return db.query(models.DataSource).all()

# Indicator CRUD
def create_indicator(db: Session, indicator: schemas.IndicatorCreate):
    db_indicator = models.Indicator(
        name=indicator.name,
        synonyms=indicator.synonyms,
        unit=indicator.unit,
        evaluation_criteria=indicator.evaluation_criteria,
        formula=indicator.formula,
        table_name=indicator.table_name,
        data_source_id=indicator.data_source_id
    )
    db.add(db_indicator)
    db.commit()
    db.refresh(db_indicator)

    for field in indicator.fields:
        db_field = models.IndicatorField(**field.dict(), indicator_id=db_indicator.id)
        db.add(db_field)
    
    db.commit()
    db.refresh(db_indicator)
    return db_indicator

def get_indicators(db: Session):
    return db.query(models.Indicator).all()

def get_indicator_by_name(db: Session, name: str):
    return db.query(models.Indicator).filter(models.Indicator.name == name).first()

# Agent CRUD
def create_agent(db: Session, agent: schemas.AgentCreate):
    db_agent = models.Agent(name=agent.name, description=agent.description)
    if agent.indicator_ids:
        indicators = db.query(models.Indicator).filter(models.Indicator.id.in_(agent.indicator_ids)).all()
        db_agent.indicators = indicators
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def get_agents(db: Session):
    return db.query(models.Agent).all()

# SOP CRUD
def create_sop(db: Session, sop: schemas.SOPCreate):
    db_sop = models.SOP(name=sop.name, description=sop.description, report_template=sop.report_template)
    db.add(db_sop)
    db.commit()
    db.refresh(db_sop)

    for task in sop.tasks:
        db_task = models.SOPTask(**task.dict(), sop_id=db_sop.id)
        db.add(db_task)
    
    db.commit()
    db.refresh(db_sop)
    return db_sop

def get_sops(db: Session):
    return db.query(models.SOP).all()
