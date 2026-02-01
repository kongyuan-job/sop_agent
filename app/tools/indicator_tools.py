from langchain.tools import tool
from ..db import SessionLocal
from ..models import database as models
from ..services import metadata_service
from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime, timedelta
import json

@tool
def query_indicator_semantics(indicator_name: str) -> str:
    """Queries the semantic information of an indicator by its name. 
    Returns basic info, fields, and relationships."""
    db = SessionLocal()
    try:
        indicator = db.query(models.Indicator).filter(models.Indicator.name == indicator_name).first()
        if not indicator:
            return f"Indicator '{indicator_name}' not found."
        
        info = {
            "name": indicator.name,
            "synonyms": indicator.synonyms,
            "unit": indicator.unit,
            "evaluation_criteria": indicator.evaluation_criteria,
            "formula": indicator.formula,
            "fields": [
                {
                    "name": f.name,
                    "type": f.data_type,
                    "description": f.description,
                    "role": f.field_role,
                    "time_format": f.time_format
                } for f in indicator.fields
            ]
        }
        
        # Get relationships (simplified)
        children = db.query(models.Indicator).join(
            models.IndicatorRelation, models.Indicator.id == models.IndicatorRelation.child_id
        ).filter(models.IndicatorRelation.parent_id == indicator.id).all()
        
        parents = db.query(models.Indicator).join(
            models.IndicatorRelation, models.Indicator.id == models.IndicatorRelation.parent_id
        ).filter(models.IndicatorRelation.child_id == indicator.id).all()
        
        info["children"] = [c.name for c in children]
        info["parents"] = [p.name for p in parents]
        
        return json.dumps(info, ensure_ascii=False, indent=2)
    finally:
        db.close()

@tool
def query_indicator_value(indicator_name: str, time_value: str, dimension_filters: dict = None) -> str:
    """Queries the value of an indicator for a specific time and dimensions.
    Returns current value, YoY, MoM, and sub-indicator values.
    time_value should be in the format specified by the indicator's time dimension (e.g., '2023-10').
    dimension_filters is an optional dictionary of {dimension_name: value}."""
    db = SessionLocal()
    try:
        indicator = db.query(models.Indicator).filter(models.Indicator.name == indicator_name).first()
        if not indicator:
            return f"Indicator '{indicator_name}' not found."
        
        ds = indicator.data_source
        if ds.db_type == "sqlite":
            url = f"sqlite:///{ds.host}"
        else:
            url = f"{ds.db_type}://{ds.username}:{ds.password}@{ds.host}:{ds.port}/{ds.database}"
        
        engine = create_engine(url)
        
        # Find time field and measure field
        time_field = next((f for f in indicator.fields if f.field_role == "TIME"), None)
        measure_field = next((f for f in indicator.fields if f.field_role == "MEASURE"), None)
        
        if not time_field or not measure_field:
            return "Indicator definition missing TIME or MEASURE fields."

        # Build query for current value
        where_clause = f"WHERE {time_field.name} = '{time_value}'"
        if dimension_filters:
            for k, v in dimension_filters.items():
                where_clause += f" AND {k} = '{v}'"
        
        query = f"SELECT SUM({measure_field.name}) as value FROM {indicator.table_name} {where_clause}"
        df_current = pd.read_sql(query, engine)
        current_val = df_current['value'].iloc[0] if not df_current.empty else None
        
        if current_val is None:
            return f"No data found for {indicator_name} at {time_value}."

        # Calculate MoM (Month over Month) - simplified logic for demo
        # Assuming yyyy-MM format
        try:
            cur_dt = datetime.strptime(time_value, "%Y-%m")
            last_month_dt = (cur_dt.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_month_val_str = last_month_dt.strftime("%Y-%m")
            
            query_mom = f"SELECT SUM({measure_field.name}) as value FROM {indicator.table_name} WHERE {time_field.name} = '{last_month_val_str}'"
            if dimension_filters:
                for k, v in dimension_filters.items():
                    query_mom += f" AND {k} = '{v}'"
            df_mom = pd.read_sql(query_mom, engine)
            mom_val = df_mom['value'].iloc[0] if not df_mom.empty else None
            mom_rate = (current_val - mom_val) / mom_val if mom_val and mom_val != 0 else None
        except:
            mom_rate = None

        # Calculate YoY (Year over Year)
        try:
            last_year_dt = cur_dt.replace(year=cur_dt.year - 1)
            last_year_val_str = last_year_dt.strftime("%Y-%m")
            query_yoy = f"SELECT SUM({measure_field.name}) as value FROM {indicator.table_name} WHERE {time_field.name} = '{last_year_val_str}'"
            if dimension_filters:
                for k, v in dimension_filters.items():
                    query_yoy += f" AND {k} = '{v}'"
            df_yoy = pd.read_sql(query_yoy, engine)
            yoy_val = df_yoy['value'].iloc[0] if not df_yoy.empty else None
            yoy_rate = (current_val - yoy_val) / yoy_val if yoy_val and yoy_val != 0 else None
        except:
            yoy_rate = None

        result = {
            "indicator": indicator_name,
            "time": time_value,
            "unit": indicator.unit,
            "value": float(current_val),
            "mom_rate": mom_rate,
            "yoy_rate": yoy_rate,
            "evaluation": indicator.evaluation_criteria
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error querying indicator value: {str(e)}"
    finally:
        db.close()
