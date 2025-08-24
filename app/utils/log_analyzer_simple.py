"""
Simplified log analysis and monitoring utilities.

Provides basic log analysis and monitoring capabilities 
for the FastAPI application with comprehensive logging.
"""

import json
import statistics
from collections import Counter, defaultdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from app.core.advanced_logging import LogEntry
from app.db.session import SessionLocal


class LogAnalyzer:
    """Analyze application logs for insights and patterns."""

    def __init__(self, db: Session):
        self.db = db
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the last N hours."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Query error logs from database
        error_logs = (
            self.db.query(LogEntry)
            .filter(
                and_(
                    LogEntry.level.in_(["ERROR", "CRITICAL"]),
                    LogEntry.timestamp >= since
                )
            )
            .order_by(desc(LogEntry.timestamp))
            .all()
        )
        
        if not error_logs:
            return {
                "total_errors": 0,
                "error_rate": 0.0,
                "most_common_errors": {},
                "affected_modules": {},
                "period_hours": hours
            }
        
        # Analyze errors
        error_types: Counter[str] = Counter()
        error_modules: Counter[str] = Counter()
        
        for log in error_logs:
            # Use first 100 chars of message as error type
            error_type = log.message[:100] if log.message else "Unknown"
            error_types[error_type] += 1
            
            module = log.module if hasattr(log, 'module') and log.module else "unknown"
            error_modules[module] += 1
        
        return {
            "total_errors": len(error_logs),
            "error_rate": round(len(error_logs) / hours, 2),
            "most_common_errors": dict(error_types.most_common(10)),
            "affected_modules": dict(error_modules.most_common(10)),
            "period_hours": hours
        }
    
    def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze API performance metrics."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Get all logs for performance analysis
        logs = (
            self.db.query(LogEntry)
            .filter(LogEntry.timestamp >= since)
            .all()
        )
        
        if not logs:
            return {
                "total_requests": 0,
                "avg_response_time": 0,
                "period_hours": hours
            }
        
        # Simple performance metrics
        response_times = []
        request_count = 0
        
        for log in logs:
            if hasattr(log, 'extra_data') and log.extra_data:
                try:
                    # Convert extra_data to string if it's not already
                    extra_str = str(log.extra_data) if not isinstance(log.extra_data, str) else log.extra_data
                    extra_data = json.loads(extra_str)
                    
                    if "duration_ms" in extra_data:
                        response_times.append(float(extra_data["duration_ms"]))
                        request_count += 1
                except (json.JSONDecodeError, ValueError, TypeError):
                    continue
        
        if not response_times:
            return {
                "total_requests": len(logs),
                "avg_response_time": 0,
                "max_response_time": 0,
                "min_response_time": 0,
                "period_hours": hours
            }
        
        return {
            "total_requests": request_count,
            "avg_response_time": round(statistics.mean(response_times), 2),
            "max_response_time": round(max(response_times), 2),
            "min_response_time": round(min(response_times), 2),
            "period_hours": hours
        }
    
    def get_security_alerts(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze security events and generate alerts."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Look for security-related log entries
        security_logs = (
            self.db.query(LogEntry)
            .filter(
                and_(
                    LogEntry.timestamp >= since,
                    or_(
                        LogEntry.message.contains("security"),
                        LogEntry.message.contains("unauthorized"),
                        LogEntry.message.contains("forbidden"),
                        LogEntry.message.contains("suspicious"),
                        LogEntry.level == "WARNING"
                    )
                )
            )
            .all()
        )
        
        security_events: Counter[str] = Counter()
        for log in security_logs:
            event_type = "unknown"
            if "unauthorized" in log.message.lower():
                event_type = "unauthorized_access"
            elif "forbidden" in log.message.lower():
                event_type = "forbidden_access"
            elif "suspicious" in log.message.lower():
                event_type = "suspicious_activity"
            
            security_events[event_type] += 1
        
        return {
            "total_security_events": len(security_logs),
            "event_types": dict(security_events.most_common()),
            "period_hours": hours
        }
    
    def get_user_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get user activity summary."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Get logs with user information
        user_logs = (
            self.db.query(LogEntry)
            .filter(
                and_(
                    LogEntry.timestamp >= since,
                    LogEntry.user_id.isnot(None)
                )
            )
            .all()
        )
        
        if not user_logs:
            return {
                "total_user_actions": 0,
                "unique_users": 0,
                "period_hours": hours
            }
        
        unique_users = set()
        for log in user_logs:
            if hasattr(log, 'user_id') and log.user_id:
                unique_users.add(str(log.user_id))
        
        return {
            "total_user_actions": len(user_logs),
            "unique_users": len(unique_users),
            "period_hours": hours
        }


class LogMonitor:
    """Monitor logs for real-time alerts and anomalies."""

    def __init__(self, db: Session):
        self.db = db
    
    def check_error_rate_alert(self, minutes: int = 5) -> Optional[Dict[str, Any]]:
        """Check if error rate is above threshold."""
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        error_count = (
            self.db.query(LogEntry)
            .filter(
                and_(
                    LogEntry.timestamp >= since,
                    LogEntry.level.in_(["ERROR", "CRITICAL"])
                )
            )
            .count()
        )
        
        # Alert if more than 10 errors in 5 minutes
        threshold = 10
        if error_count > threshold:
            return {
                "alert_type": "high_error_rate",
                "severity": "critical",
                "error_count": error_count,
                "threshold": threshold,
                "time_window_minutes": minutes,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        return None
    
    def check_security_alerts(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Check for security-related alerts."""
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        alerts = []
        
        # Check for multiple failed authentication attempts
        failed_auth_count = (
            self.db.query(LogEntry)
            .filter(
                and_(
                    LogEntry.timestamp >= since,
                    LogEntry.message.contains("authentication failed")
                )
            )
            .count()
        )
        
        if failed_auth_count > 5:
            alerts.append({
                "alert_type": "multiple_failed_auth",
                "severity": "warning",
                "failed_attempts": failed_auth_count,
                "time_window_minutes": minutes,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return alerts
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate a comprehensive daily report."""
        analyzer = LogAnalyzer(self.db)
        
        return {
            "report_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "errors": analyzer.get_error_summary(hours=24),
            "performance": analyzer.get_performance_metrics(hours=24),
            "security": analyzer.get_security_alerts(hours=24),
            "user_activity": analyzer.get_user_activity_summary(hours=24)
        }
