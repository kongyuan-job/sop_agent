from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Many-to-Many relationship between Agents and Indicators
agent_indicators = Table(
    "agent_indicators",
    Base.metadata,
    Column("agent_id", Integer, ForeignKey("agents.id"), primary_key=True),
    Column("indicator_id", Integer, ForeignKey("indicators.id"), primary_key=True),
)

class DataSource(Base):
    __tablename__ = "data_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    db_type = Column(String(50))  # e.g., postgresql, mysql, sqlite
    host = Column(String(255))
    port = Column(Integer)
    database = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))

class Indicator(Base):
    __tablename__ = "indicators"
    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"))
    name = Column(String(255), unique=True, index=True)
    synonyms = Column(Text)  # Comma separated or JSON
    unit = Column(String(50))
    evaluation_criteria = Column(Text)
    formula = Column(Text)
    table_name = Column(String(255))

    data_source = relationship("DataSource")
    fields = relationship("IndicatorField", back_populates="indicator", cascade="all, delete-orphan")

class IndicatorField(Base):
    __tablename__ = "indicator_fields"
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"))
    name = Column(String(255))
    data_type = Column(String(50))
    description = Column(Text)
    field_role = Column(String(50))  # MEASURE, TIME, DIMENSION
    time_format = Column(String(50))  # e.g., yyyy-MM-dd

    indicator = relationship("Indicator", back_populates="fields")

class IndicatorRelation(Base):
    __tablename__ = "indicator_relations"
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("indicators.id"))
    child_id = Column(Integer, ForeignKey("indicators.id"))

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(Text)
    
    indicators = relationship("Indicator", secondary=agent_indicators)

class SOP(Base):
    __tablename__ = "sops"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(Text)
    report_template = Column(Text)
    
    tasks = relationship("SOPTask", back_populates="sop", cascade="all, delete-orphan")

class SOPTask(Base):
    __tablename__ = "sop_tasks"
    id = Column(Integer, primary_key=True, index=True)
    sop_id = Column(Integer, ForeignKey("sops.id"))
    name = Column(String(255))
    detail = Column(Text)
    tools = Column(JSON)  # List of tool names
    dependencies = Column(JSON)  # List of parent task IDs or names

    sop = relationship("SOP", back_populates="tasks")
