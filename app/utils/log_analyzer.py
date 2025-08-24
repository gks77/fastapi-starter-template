"""
Advanced log analysis and monitoring utilities.

Provides comprehensive log analysis, alerting, and monitoring capabilities
for tracking application performance, errors, and security events.
"""

import os
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
    """Comprehensive log analysis and monitoring tool."""
    
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
        
        # Analyze errors
        error_types = Counter()
        error_modules = Counter()
        error_timeline = defaultdict(int)
        
        for log in error_logs:
            error_types[log.message] += 1
            error_modules[log.module] += 1
            
            # Group by hour for timeline
            hour_key = log.timestamp.strftime("%Y-%m-%d %H:00")
            error_timeline[hour_key] += 1
        
        return {
            "total_errors": len(error_logs),
            "time_period_hours": hours,
            "most_common_errors": dict(error_types.most_common(10)),
            "affected_modules": dict(error_modules.most_common(10)),
            "error_timeline": dict(error_timeline),
            "recent_errors": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "message": log.message,
                    "module": log.module,
                    "function": log.function
                }
                for log in error_logs[:20]
            ]
        }
    
    def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze API performance metrics."""
        # This would typically read from file logs or Elasticsearch
        # For now, we'll simulate with database data
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Get performance-related logs
        perf_logs = (
            self.db.query(LogEntry)
            .filter(
                and_(
                    LogEntry.extra_data.contains("api_performance"),
                    LogEntry.timestamp >= since
                )
            )
            .all()
        )
        
        endpoint_stats = defaultdict(list)
        
        for log in perf_logs:
            if log.extra_data:
                try:
                    extra_data = json.loads(log.extra_data)
                    if extra_data.get("event_type") == "api_performance":
                        endpoint = extra_data.get("endpoint", "unknown")
                        duration = extra_data.get("duration_ms", 0)
                        endpoint_stats[endpoint].append(duration)
                except json.JSONDecodeError:
                    continue
        
        # Calculate statistics
        performance_summary = {}
        for endpoint, durations in endpoint_stats.items():
            if durations:
                performance_summary[endpoint] = {
                    "requests": len(durations),
                    "avg_response_time_ms": sum(durations) / len(durations),
                    "max_response_time_ms": max(durations),
                    "min_response_time_ms": min(durations),
                    "p95_response_time_ms": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0]
                }
        
        return {
            "time_period_hours": hours,
            "total_requests": sum(len(durations) for durations in endpoint_stats.values()),
            "endpoints_analyzed": len(endpoint_stats),
            "performance_by_endpoint": performance_summary
        }
    
    def get_security_alerts(self, hours: int = 24) -> Dict[str, Any]:
        """Get security-related alerts."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        security_logs = (
            self.db.query(LogEntry)
            .filter(
                and_(
                    LogEntry.extra_data.contains("security_event"),
                    LogEntry.timestamp >= since
                )
            )
            .order_by(desc(LogEntry.timestamp))
            .all()
        )
        
        security_events = []
        event_types = Counter()
        severity_counts = Counter()
        
        for log in security_logs:
            if log.extra_data:
                try:
                    extra_data = json.loads(log.extra_data)
                    if extra_data.get("event_type") == "security_event":
                        event_type = extra_data.get("security_event_type", "unknown")
                        severity = extra_data.get("severity", "unknown")
                        
                        event_types[event_type] += 1
                        severity_counts[severity] += 1
                        
                        security_events.append({
                            "timestamp": log.timestamp.isoformat(),
                            "event_type": event_type,
                            "severity": severity,
                            "message": log.message,
                            "details": extra_data
                        })
                except json.JSONDecodeError:
                    continue
        
        return {
            "total_security_events": len(security_events),
            "time_period_hours": hours,
            "event_types": dict(event_types),
            "severity_distribution": dict(severity_counts),
            "recent_events": security_events[:50]
        }
    
    def get_user_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze user activity patterns."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        user_logs = (
            self.db.query(LogEntry)
            .filter(
                and_(
                    LogEntry.user_id.isnot(None),
                    LogEntry.timestamp >= since
                )
            )
            .all()
        )
        
        user_activity = defaultdict(int)
        activity_timeline = defaultdict(int)
        
        for log in user_logs:
            user_activity[log.user_id] += 1
            
            # Group by hour
            hour_key = log.timestamp.strftime("%Y-%m-%d %H:00")
            activity_timeline[hour_key] += 1
        
        return {
            "total_user_actions": len(user_logs),
            "unique_users": len(user_activity),
            "time_period_hours": hours,
            "most_active_users": dict(Counter(user_activity).most_common(20)),
            "activity_timeline": dict(activity_timeline)
        }


class LogMonitor:
    """Real-time log monitoring and alerting."""
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_thresholds = {
            "error_rate_per_minute": 10,
            "avg_response_time_ms": 5000,
            "failed_login_attempts_per_minute": 5
        }
    
    def check_error_rate_alert(self, minutes: int = 5) -> Optional[Dict[str, Any]]:
        """Check if error rate exceeds threshold."""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        error_count = (
            self.db.query(LogEntry)
            .filter(
                and_(
                    LogEntry.level.in_(["ERROR", "CRITICAL"]),
                    LogEntry.timestamp >= since
                )
            )
            .count()
        )
        
        error_rate = error_count / minutes
        
        if error_rate > self.alert_thresholds["error_rate_per_minute"]:
            return {
                "alert_type": "high_error_rate",
                "severity": "high",
                "error_count": error_count,
                "time_period_minutes": minutes,
                "rate_per_minute": error_rate,
                "threshold": self.alert_thresholds["error_rate_per_minute"],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return None
    
    def check_security_alerts(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Check for security-related alerts."""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        alerts = []
        
        # Check for multiple failed login attempts
        failed_logins = (
            self.db.query(LogEntry)
            .filter(
                and_(
                    LogEntry.extra_data.contains("authentication_failure"),
                    LogEntry.timestamp >= since
                )
            )
            .count()
        )
        
        if failed_logins > self.alert_thresholds["failed_login_attempts_per_minute"] * minutes:
            alerts.append({
                "alert_type": "multiple_failed_logins",
                "severity": "medium",
                "failed_attempts": failed_logins,
                "time_period_minutes": minutes,
                "rate_per_minute": failed_logins / minutes,
                "threshold": self.alert_thresholds["failed_login_attempts_per_minute"],
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate comprehensive daily report."""
        analyzer = LogAnalyzer(self.db)
        
        return {
            "report_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "generated_at": datetime.utcnow().isoformat(),
            "error_summary": analyzer.get_error_summary(24),
            "performance_metrics": analyzer.get_performance_metrics(24),
            "security_summary": analyzer.get_security_alerts(24),
            "user_activity": analyzer.get_user_activity_summary(24)
        }
