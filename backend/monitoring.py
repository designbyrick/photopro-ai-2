"""
Monitoring and health check utilities for PhotoPro AI.
Provides comprehensive system monitoring and alerting.
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from database import get_db
from models import User, GeneratedPhoto, CreditTransaction
from fastapi import Depends, HTTPException
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring and health checks"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.request_count = 0
        self.error_count = 0
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process information
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round((disk.used / disk.total) * 100, 2)
                },
                "process": {
                    "memory_mb": round(process_memory.rss / (1024**2), 2),
                    "cpu_percent": process.cpu_percent()
                }
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}
    
    def get_application_metrics(self, db: Session) -> Dict[str, Any]:
        """Get application-specific metrics"""
        try:
            # Database metrics
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            total_photos = db.query(GeneratedPhoto).count()
            completed_photos = db.query(GeneratedPhoto).filter(
                GeneratedPhoto.status == "completed"
            ).count()
            
            # Recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_users = db.query(User).filter(User.created_at >= yesterday).count()
            recent_photos = db.query(GeneratedPhoto).filter(
                GeneratedPhoto.created_at >= yesterday
            ).count()
            
            # Credit metrics
            total_credits_used = db.query(CreditTransaction).filter(
                CreditTransaction.amount < 0
            ).count()
            
            return {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "recent_signups": recent_users
                },
                "photos": {
                    "total": total_photos,
                    "completed": completed_photos,
                    "recent_generations": recent_photos,
                    "success_rate": round((completed_photos / total_photos * 100), 2) if total_photos > 0 else 0
                },
                "credits": {
                    "total_transactions": total_credits_used
                }
            }
        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return {"error": str(e)}
    
    def check_database_health(self, db: Session) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            db.execute("SELECT 1")
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def check_external_services(self) -> Dict[str, Any]:
        """Check external service connectivity"""
        services = {}
        
        # Check AWS S3
        try:
            import boto3
            from config import settings
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            s3_client.head_bucket(Bucket=settings.AWS_BUCKET_NAME)
            services["s3"] = {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            services["s3"] = {"status": "unhealthy", "error": str(e)}
        
        # Check Replicate API
        try:
            import replicate
            from config import settings
            
            client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)
            # Simple API call to test connectivity
            models = client.models.list()
            services["replicate"] = {"status": "healthy", "response_time_ms": 0}
        except Exception as e:
            services["replicate"] = {"status": "unhealthy", "error": str(e)}
        
        return services
    
    def get_health_status(self, db: Session) -> Dict[str, Any]:
        """Get overall health status"""
        system_metrics = self.get_system_metrics()
        app_metrics = self.get_application_metrics(db)
        db_health = self.check_database_health(db)
        external_services = self.check_external_services()
        
        # Determine overall health
        overall_status = "healthy"
        issues = []
        
        # Check database
        if db_health.get("status") != "healthy":
            overall_status = "unhealthy"
            issues.append("Database connectivity issues")
        
        # Check external services
        for service, status in external_services.items():
            if status.get("status") != "healthy":
                overall_status = "degraded"
                issues.append(f"{service.upper()} service issues")
        
        # Check system resources
        if system_metrics.get("memory", {}).get("used_percent", 0) > 90:
            overall_status = "degraded"
            issues.append("High memory usage")
        
        if system_metrics.get("cpu_percent", 0) > 90:
            overall_status = "degraded"
            issues.append("High CPU usage")
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "issues": issues,
            "system": system_metrics,
            "application": app_metrics,
            "database": db_health,
            "external_services": external_services
        }

# Global monitor instance
monitor = SystemMonitor()

def get_system_metrics():
    """Get current system metrics"""
    return monitor.get_system_metrics()

def get_application_metrics(db: Session = Depends(get_db)):
    """Get application metrics"""
    return monitor.get_application_metrics(db)

def get_health_status(db: Session = Depends(get_db)):
    """Get comprehensive health status"""
    return monitor.get_health_status(db)

def get_detailed_health():
    """Get detailed health information for monitoring"""
    db = next(get_db())
    try:
        return monitor.get_health_status(db)
    finally:
        db.close()

# Alert thresholds
ALERT_THRESHOLDS = {
    "cpu_percent": 80,
    "memory_percent": 85,
    "disk_percent": 90,
    "response_time_ms": 5000
}

def check_alert_conditions(metrics: Dict[str, Any]) -> list:
    """Check if any metrics exceed alert thresholds"""
    alerts = []
    
    cpu_percent = metrics.get("system", {}).get("cpu_percent", 0)
    if cpu_percent > ALERT_THRESHOLDS["cpu_percent"]:
        alerts.append(f"High CPU usage: {cpu_percent}%")
    
    memory_percent = metrics.get("system", {}).get("memory", {}).get("used_percent", 0)
    if memory_percent > ALERT_THRESHOLDS["memory_percent"]:
        alerts.append(f"High memory usage: {memory_percent}%")
    
    disk_percent = metrics.get("system", {}).get("disk", {}).get("used_percent", 0)
    if disk_percent > ALERT_THRESHOLDS["disk_percent"]:
        alerts.append(f"High disk usage: {disk_percent}%")
    
    db_response_time = metrics.get("database", {}).get("response_time_ms", 0)
    if db_response_time > ALERT_THRESHOLDS["response_time_ms"]:
        alerts.append(f"Slow database response: {db_response_time}ms")
    
    return alerts
