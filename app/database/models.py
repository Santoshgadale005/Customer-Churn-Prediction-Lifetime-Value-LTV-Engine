from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Float,
    String
)
from datetime import datetime
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_prediction_logs_churn_probability", "churn_probability"),
        Index("idx_prediction_logs_customer_segment", "customer_segment"),
        Index("idx_prediction_logs_created_at", "created_at"),
        Index("idx_prediction_logs_user_id", "user_id"),
    )
