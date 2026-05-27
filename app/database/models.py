from sqlalchemy import (
    Column,
    Integer,
    Float,
    String
)
from app.database.database import Base

class PredictionLog(Base):
    __tablename__ = "prediction_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    gender = Column(String)
    tenure = Column(Integer)
    monthly_charges = Column(Float)
    total_charges = Column(Float)
    prediction = Column(Integer)
    churn_probability = Column(Float)
    predicted_ltv = Column(Float)
    customer_segment = Column(String)
    recommendation = Column(String)
