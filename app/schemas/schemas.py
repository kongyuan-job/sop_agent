from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Data Source
class DataSourceBase(BaseModel):
    name: str
    db_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class DataSourceCreate(DataSourceBase):
    pass

class DataSource(DataSourceBase):
    id: int
    class Config:
        orm_mode = True

# Indicator Field
class IndicatorFieldBase(BaseModel):
    name: str
    data_type: str
    description: Optional[str] = None
    field_role: str # MEASURE, TIME, DIMENSION
    time_format: Optional[str] = None

class IndicatorFieldCreate(IndicatorFieldBase):
    pass

class IndicatorField(IndicatorFieldBase):
    id: int
    indicator_id: int
    class Config:
        orm_mode = True

# Indicator
class IndicatorBase(BaseModel):
    name: str
    synonyms: Optional[str] = None
    unit: Optional[str] = None
    evaluation_criteria: Optional[str] = None
    formula: Optional[str] = None
    table_name: Optional[str] = None
    data_source_id: int

class IndicatorCreate(IndicatorBase):
    fields: List[IndicatorFieldCreate] = []

class Indicator(IndicatorBase):
    id: int
    fields: List[IndicatorField] = []
    class Config:
        orm_mode = True

# Agent
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None

class AgentCreate(AgentBase):
    indicator_ids: List[int] = []

class Agent(AgentBase):
    id: int
    indicators: List[Indicator] = []
    class Config:
        orm_mode = True

# SOP Task
class SOPTaskBase(BaseModel):
    name: str
    detail: str
    tools: List[str] = []
    dependencies: List[str] = []

class SOPTaskCreate(SOPTaskBase):
    pass

class SOPTask(SOPTaskBase):
    id: int
    class Config:
        orm_mode = True

# SOP
class SOPBase(BaseModel):
    name: str
    description: str
    report_template: Optional[str] = None

class SOPCreate(SOPBase):
    tasks: List[SOPTaskCreate] = []

class SOP(SOPBase):
    id: int
    tasks: List[SOPTask] = []
    class Config:
        orm_mode = True

# Indicator Query Response (Used for Tools)
class IndicatorValueResult(BaseModel):
    indicator_name: str
    current_value: float
    yoy: Optional[float] = None # Year-on-Year
    mom: Optional[float] = None # Month-on-Month
    sub_indicators: List[Dict[str, Any]] = []
