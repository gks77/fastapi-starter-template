"""
API endpoints for log monitoring and analysis.

Provides REST API endpoints to access log analytics, monitoring data,
and generate reports for system administrators.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.api import deps
from app.models.user import User
from app.utils.log_analyzer_simple import LogAnalyzer, LogMonitor
from app.db.session import get_db

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_superuser)
):
    """Get overall system health status."""
    monitor = LogMonitor(db)
    
    # Check for recent alerts
    error_alert = monitor.check_error_rate_alert(minutes=5)
    security_alerts = monitor.check_security_alerts(minutes=10)
    
    health_status = "healthy"
    if error_alert or security_alerts:
        health_status = "warning" if not error_alert else "critical"
    
    return {
        "status": health_status,
        "timestamp": datetime.utcnow().isoformat(),
        "error_alert": error_alert,
        "security_alerts": security_alerts,
        "system_uptime": "Available via separate endpoint"
    }


@router.get("/errors", response_model=Dict[str, Any])
async def get_error_analysis(
    hours: int = Query(default=24, le=168, description="Hours to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_superuser)
):
    """Get detailed error analysis for the specified time period."""
    try:
        analyzer = LogAnalyzer(db)
        return analyzer.get_error_summary(hours=hours)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing logs: {str(e)}"
        )


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    hours: int = Query(default=24, le=168, description="Hours to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_superuser)
):
    """Get API performance metrics for the specified time period."""
    try:
        analyzer = LogAnalyzer(db)
        return analyzer.get_performance_metrics(hours=hours)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing performance: {str(e)}"
        )


@router.get("/security", response_model=Dict[str, Any])
async def get_security_analysis(
    hours: int = Query(default=24, le=168, description="Hours to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_superuser)
):
    """Get security event analysis for the specified time period."""
    try:
        analyzer = LogAnalyzer(db)
        return analyzer.get_security_alerts(hours=hours)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing security events: {str(e)}"
        )


@router.get("/users/activity", response_model=Dict[str, Any])
async def get_user_activity(
    hours: int = Query(default=24, le=168, description="Hours to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_superuser)
):
    """Get user activity analysis for the specified time period."""
    try:
        analyzer = LogAnalyzer(db)
        return analyzer.get_user_activity_summary(hours=hours)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing user activity: {str(e)}"
        )


@router.get("/report/daily", response_model=Dict[str, Any])
async def get_daily_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_superuser)
):
    """Generate comprehensive daily system report."""
    try:
        monitor = LogMonitor(db)
        return monitor.generate_daily_report()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating daily report: {str(e)}"
        )


@router.get("/alerts/active", response_model=List[Dict[str, Any]])
async def get_active_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_superuser)
):
    """Get all currently active alerts."""
    try:
        monitor = LogMonitor(db)
        
        alerts = []
        
        # Check error rate alerts
        error_alert = monitor.check_error_rate_alert(minutes=5)
        if error_alert:
            alerts.append(error_alert)
        
        # Check security alerts
        security_alerts = monitor.check_security_alerts(minutes=10)
        alerts.extend(security_alerts)
        
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking alerts: {str(e)}"
        )


@router.get("/search", response_model=Dict[str, Any])
async def search_logs(
    query: str = Query(..., description="Search query"),
    level: Optional[str] = Query(None, description="Log level filter"),
    hours: int = Query(default=24, le=168, description="Hours to search"),
    limit: int = Query(default=100, le=1000, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_superuser)
):
    """Search logs with filters."""
    try:
        from app.core.advanced_logging import LogEntry
        from sqlalchemy import and_, or_
        from datetime import timedelta
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query
        query_conditions = [LogEntry.timestamp >= since]
        
        # Add search conditions
        if query:
            query_conditions.append(
                or_(
                    LogEntry.message.contains(query),
                    LogEntry.module.contains(query),
                    LogEntry.function.contains(query)
                )
            )
        
        if level:
            query_conditions.append(LogEntry.level == level.upper())
        
        # Execute search
        logs = (
            db.query(LogEntry)
            .filter(and_(*query_conditions))
            .order_by(LogEntry.timestamp.desc())
            .limit(limit)
            .all()
        )
        
        # Format results
        results = []
        for log in logs:
            results.append({
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "logger": log.logger_name,
                "message": log.message,
                "module": log.module,
                "function": log.function,
                "line": log.line_number,
                "user_id": log.user_id,
                "request_id": log.request_id
            })
        
        return {
            "query": query,
            "filters": {"level": level, "hours": hours},
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching logs: {str(e)}"
        )
