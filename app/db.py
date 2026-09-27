import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, JSON, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./evalops.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EvalRun(Base):
    __tablename__ = "eval_runs"
    id = Column(Integer, primary_key=True, index=True)
    suite_name = Column(String, nullable=False)
    model = Column(String, nullable=False)
    total_cases = Column(Integer, default=0)
    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    total_cost_usd = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EvalCase(Base):
    __tablename__ = "eval_cases"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, index=True, nullable=False)
    case_id = Column(String, nullable=False)
    input = Column(String, nullable=False)
    expected = Column(String, nullable=False)
    output = Column(String, default="")
    score = Column(Float, default=0.0)
    raw_similarity = Column(Float, nullable=True)
    passed = Column(Boolean, default=False)
    latency_ms = Column(Integer, default=0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    error = Column(String, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()