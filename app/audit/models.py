from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from datetime import datetime, timezone
from app.database import Base

class AuditLog(Base):
    """Таблиця аудиту безпеки за правилом 5W."""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=False)
    action = Column(String(50), nullable=False)
    resource = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    http_method = Column(String(10), nullable=True)
    endpoint = Column(String(200), nullable=True)
    status_code = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False)
    details = Column(Text, nullable=True)

Index("ix_audit_action_ts", AuditLog.action, AuditLog.timestamp)
Index("ix_audit_user_ts", AuditLog.user_id, AuditLog.timestamp)
Index("ix_audit_ip_action", AuditLog.ip_address, AuditLog.action)
