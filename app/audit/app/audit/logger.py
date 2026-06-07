import json
import logging
from sqlalchemy.orm import Session
from app.audit.models import AuditLog

logger = logging.getLogger("security_audit")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def log_event(db: Session, action: str, status: str, ip_address: str,
              user_id=None, username=None, http_method=None,
              endpoint=None, status_code=None, resource=None, details=None):
    
    log_entry = AuditLog(
        user_id=user_id, username=username, ip_address=ip_address,
        action=action, status=status, http_method=http_method,
        endpoint=endpoint, status_code=status_code, resource=resource,
        details=json.dumps(details, ensure_ascii=False) if details else None,
    )
    db.add(log_entry)
    db.commit()

    log_data = {"event_type": action, "status": status, "user_id": user_id, "ip_address": ip_address}
    level = logging.WARNING if status == "failure" else logging.INFO
    logger.log(level, json.dumps(log_data, ensure_ascii=False))

def log_login_success(db, user_id, username, ip):
    log_event(db, action="login_success", status="success", user_id=user_id, username=username, ip_address=ip, http_method="POST", endpoint="/auth/login", status_code=200)

def log_login_failed(db, username, ip, reason="invalid_credentials"):
    log_event(db, action="login_failed", status="failure", username=username, ip_address=ip, http_method="POST", endpoint="/auth/login", status_code=401, details={"reason": reason})

def log_access_denied(db, user_id, username, ip, endpoint):
    log_event(db, action="access_denied", status="failure", user_id=user_id, username=username, ip_address=ip, endpoint=endpoint, status_code=403)
