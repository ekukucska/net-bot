from sqlalchemy.orm import Session
from .models import ActionLog
from typing import List, Optional
from datetime import datetime, timedelta
import json


def create_action_log(
    db: Session,
    action: str,
    parameters: dict,
    result_summary: str,
    status: str
) -> ActionLog:
    """
    Create a new action log entry.
    """
    log_entry = ActionLog(
        action=action,
        parameters=json.dumps(parameters),
        result_summary=result_summary,
        status=status,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def get_recent_logs(db: Session, limit: int = 50) -> List[ActionLog]:
    """
    Get recent action logs.
    """
    return db.query(ActionLog).order_by(
        ActionLog.timestamp.desc()
    ).limit(limit).all()


def get_logs_by_action(db: Session, action: str, limit: int = 20) -> List[ActionLog]:
    """
    Get logs for a specific action type.
    """
    return db.query(ActionLog).filter(
        ActionLog.action == action
    ).order_by(
        ActionLog.timestamp.desc()
    ).limit(limit).all()


def get_logs_by_date_range(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> List[ActionLog]:
    """
    Get logs within a date range.
    """
    return db.query(ActionLog).filter(
        ActionLog.timestamp >= start_date,
        ActionLog.timestamp <= end_date
    ).order_by(ActionLog.timestamp.desc()).all()


def delete_old_logs(db: Session, days: int = 30) -> int:
    """
    Delete logs older than specified days.
    Returns the number of deleted records.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    count = db.query(ActionLog).filter(
        ActionLog.timestamp < cutoff_date
    ).delete()
    db.commit()
    return count
