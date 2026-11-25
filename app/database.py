from datetime import datetime
from sqlalchemy import create_engine, Integer, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.config import settings

engine = create_engine(settings.mysql_url, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class ForecastLog(Base):
    __tablename__ = "forecast_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    request_text: Mapped[str] = mapped_column(Text)
    response_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="success")

def init_db():
    Base.metadata.create_all(bind=engine)
