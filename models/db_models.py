from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from datetime import datetime
from core.database import Base

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    industry = Column(String(64), default="E-commerce & Retail")
    currency = Column(String(10), default="USD")
    currency_symbol = Column(String(5), default="$")
    target_budget = Column(Float, default=150000.0)
    reporting_period = Column(String(64), default="Last 6 Months (H1)")
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CampaignRecord(Base):
    __tablename__ = "campaign_records"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    date = Column(String(20), index=True)
    campaign_id = Column(String(64), index=True)
    campaign_name = Column(String(128), nullable=False)
    channel = Column(String(64), nullable=False, index=True)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)
    attributed_revenue = Column(Float, default=0.0)
    gross_margin_rate = Column(Float, default=0.60)
    cogs = Column(Float, default=0.0)
    contribution_profit = Column(Float, default=0.0)

class CustomerRecord(Base):
    __tablename__ = "customer_records"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    customer_id = Column(String(64), index=True)
    acquisition_date = Column(String(20), index=True)
    acquisition_campaign_id = Column(String(64), index=True)
    acquisition_channel = Column(String(64), index=True)
    first_touch_channel = Column(String(64))
    last_touch_channel = Column(String(64))
    journey_touchpoints = Column(String(256))
    total_orders = Column(Integer, default=1)
    total_revenue = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    acquisition_cost = Column(Float, default=0.0)
    segment = Column(String(64), default="New")
    churn_risk = Column(Float, default=0.2)
    is_churned = Column(Boolean, default=False)

class SavedOptimization(Base):
    __tablename__ = "saved_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    objective = Column(String(64))
    total_budget = Column(Float)
    recommendations_json = Column(Text)

class UploadHistory(Base):
    __tablename__ = "upload_history"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(String(64), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    filename = Column(String(256))
    file_type = Column(String(32))
    rows_imported = Column(Integer)
    rows_rejected = Column(Integer)
    quality_score = Column(Float)
    summary_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
