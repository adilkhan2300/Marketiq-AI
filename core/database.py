from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    return db

def init_db():
    from models.db_models import Workspace, CampaignRecord, CustomerRecord, SavedOptimization, UploadHistory
    Base.metadata.create_all(bind=engine)
