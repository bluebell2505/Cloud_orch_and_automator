from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class PipelineEvent(Base):
    __tablename__ = 'pipeline_events'

    id             = Column(Integer, primary_key=True, autoincrement=True)
    repo           = Column(String)
    run_id         = Column(String)
    failure_type   = Column(String)
    root_cause     = Column(String)
    fix_type       = Column(String)
    confidence     = Column(Float)
    fix_successful = Column(Boolean)
    action_taken   = Column(String)
    time_to_fix    = Column(Integer)
    created_at     = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f'<PipelineEvent {self.id} {self.failure_type} {self.action_taken}>'