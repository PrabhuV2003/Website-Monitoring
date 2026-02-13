"""
Database Module
===============
Handles database operations for storing monitoring results.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class MonitorCheck(Base):
    """Represents a single monitoring check run."""
    __tablename__ = 'monitor_checks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(String(50), unique=True, nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    status = Column(String(20), default='running')  # running, completed, failed
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)
    
    results = relationship("CheckResult", back_populates="check", cascade="all, delete-orphan")


class CheckResult(Base):
    """Represents a result from a specific monitor."""
    __tablename__ = 'check_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(Integer, ForeignKey('monitor_checks.id'), nullable=False)
    monitor_type = Column(String(50), nullable=False)  # uptime, forms, links, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), nullable=False)  # success, warning, error, critical
    message = Column(Text)
    details = Column(JSON)
    severity = Column(String(20))  # critical, high, medium, low
    url = Column(String(500))
    response_time = Column(Float)
    screenshot_path = Column(String(500))
    
    check = relationship("MonitorCheck", back_populates="results")


class UptimeHistory(Base):
    """Stores uptime history for trend analysis."""
    __tablename__ = 'uptime_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    url = Column(String(500), nullable=False)
    is_up = Column(Boolean, nullable=False)
    response_time = Column(Float)
    status_code = Column(Integer)
    error_message = Column(Text)


class SSLHistory(Base):
    """Stores SSL certificate history."""
    __tablename__ = 'ssl_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    domain = Column(String(255), nullable=False)
    issuer = Column(String(255))
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    days_until_expiry = Column(Integer)
    is_valid = Column(Boolean)


class BrokenLink(Base):
    """Stores broken links found during checks."""
    __tablename__ = 'broken_links'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    check_id = Column(Integer, ForeignKey('monitor_checks.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_url = Column(String(500), nullable=False)
    target_url = Column(String(500), nullable=False)
    link_text = Column(String(255))
    status_code = Column(Integer)
    error_type = Column(String(50))  # 404, timeout, connection_error, etc.
    is_external = Column(Boolean, default=False)
    first_detected = Column(DateTime, default=datetime.utcnow)
    last_detected = Column(DateTime, default=datetime.utcnow)
    times_detected = Column(Integer, default=1)


class PerformanceMetric(Base):
    """Stores performance metrics over time."""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    url = Column(String(500), nullable=False)
    ttfb = Column(Float)  # Time to First Byte
    page_load_time = Column(Float)
    dom_content_loaded = Column(Float)
    largest_contentful_paint = Column(Float)
    cumulative_layout_shift = Column(Float)
    first_input_delay = Column(Float)
    pagespeed_score = Column(Integer)
    pagespeed_data = Column(JSON)


class AlertLog(Base):
    """Logs all alerts sent."""
    __tablename__ = 'alert_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    check_id = Column(String(50))
    alert_type = Column(String(50))  # email, slack, discord
    severity = Column(String(20))
    subject = Column(String(255))
    message = Column(Text)
    recipients = Column(JSON)
    status = Column(String(20))  # sent, failed
    error_message = Column(Text)


class Database:
    """Database manager for WordPress Monitor."""
    
    def __init__(self, db_type: str = "sqlite", sqlite_path: str = "data/monitor.db", **mysql_config):
        """
        Initialize the database connection.
        
        Args:
            db_type: Database type (sqlite or mysql)
            sqlite_path: Path to SQLite database file
            **mysql_config: MySQL connection parameters
        """
        self.db_type = db_type
        
        if db_type == "sqlite":
            db_path = Path(sqlite_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self.engine = create_engine(
                f"sqlite:///{db_path}",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        elif db_type == "mysql":
            host = mysql_config.get('host', 'localhost')
            port = mysql_config.get('port', 3306)
            database = mysql_config.get('database', 'wordpress_monitor')
            username = mysql_config.get('username', os.getenv('DB_USERNAME', 'root'))
            password = mysql_config.get('password', os.getenv('DB_PASSWORD', ''))
            self.engine = create_engine(
                f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def create_check(self, check_id: str) -> MonitorCheck:
        """Create a new monitor check record."""
        with self.get_session() as session:
            check = MonitorCheck(
                check_id=check_id,
                start_time=datetime.utcnow()
            )
            session.add(check)
            session.commit()
            session.refresh(check)
            return check
    
    def update_check(self, check_id: str, **kwargs):
        """Update a monitor check record."""
        with self.get_session() as session:
            check = session.query(MonitorCheck).filter_by(check_id=check_id).first()
            if check:
                for key, value in kwargs.items():
                    setattr(check, key, value)
                session.commit()
    
    def complete_check(self, check_id: str, issues: Dict[str, int]):
        """Mark a check as completed with issue counts."""
        with self.get_session() as session:
            check = session.query(MonitorCheck).filter_by(check_id=check_id).first()
            if check:
                check.end_time = datetime.utcnow()
                check.status = 'completed'
                check.critical_issues = issues.get('critical', 0)
                check.high_issues = issues.get('high', 0)
                check.medium_issues = issues.get('medium', 0)
                check.low_issues = issues.get('low', 0)
                check.total_issues = sum(issues.values())
                session.commit()
    
    def add_result(self, check_id: str, **result_data):
        """Add a check result."""
        with self.get_session() as session:
            check = session.query(MonitorCheck).filter_by(check_id=check_id).first()
            if check:
                # Convert ISO string timestamp to datetime if needed
                if 'timestamp' in result_data and isinstance(result_data['timestamp'], str):
                    result_data['timestamp'] = datetime.fromisoformat(result_data['timestamp'])
                result = CheckResult(check_id=check.id, **result_data)
                session.add(result)
                session.commit()
    
    def add_uptime_record(self, url: str, is_up: bool, response_time: float = None,
                          status_code: int = None, error_message: str = None):
        """Add an uptime history record."""
        with self.get_session() as session:
            record = UptimeHistory(
                url=url,
                is_up=is_up,
                response_time=response_time,
                status_code=status_code,
                error_message=error_message
            )
            session.add(record)
            session.commit()
    
    def add_ssl_record(self, domain: str, **ssl_data):
        """Add an SSL history record."""
        with self.get_session() as session:
            record = SSLHistory(domain=domain, **ssl_data)
            session.add(record)
            session.commit()
    
    def add_broken_link(self, check_id: str, source_url: str, target_url: str, **link_data):
        """Add or update a broken link record."""
        with self.get_session() as session:
            existing = session.query(BrokenLink).filter_by(
                source_url=source_url,
                target_url=target_url
            ).first()
            
            if existing:
                existing.last_detected = datetime.utcnow()
                existing.times_detected += 1
            else:
                check = session.query(MonitorCheck).filter_by(check_id=check_id).first()
                link = BrokenLink(
                    check_id=check.id if check else None,
                    source_url=source_url,
                    target_url=target_url,
                    **link_data
                )
                session.add(link)
            session.commit()
    
    def add_performance_metric(self, url: str, **metrics):
        """Add a performance metric record."""
        with self.get_session() as session:
            metric = PerformanceMetric(url=url, **metrics)
            session.add(metric)
            session.commit()
    
    def add_alert_log(self, **alert_data):
        """Log an alert."""
        with self.get_session() as session:
            alert = AlertLog(**alert_data)
            session.add(alert)
            session.commit()
    
    def get_recent_checks(self, limit: int = 10) -> List[MonitorCheck]:
        """Get recent monitor checks."""
        with self.get_session() as session:
            return session.query(MonitorCheck)\
                .order_by(MonitorCheck.start_time.desc())\
                .limit(limit)\
                .all()
    
    def get_check_results(self, check_id: str) -> List[CheckResult]:
        """Get all results for a specific check."""
        with self.get_session() as session:
            check = session.query(MonitorCheck).filter_by(check_id=check_id).first()
            if check:
                return check.results
            return []
    
    def get_uptime_history(self, url: str, days: int = 30) -> List[UptimeHistory]:
        """Get uptime history for a URL."""
        from datetime import timedelta
        with self.get_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            return session.query(UptimeHistory)\
                .filter(UptimeHistory.url == url)\
                .filter(UptimeHistory.timestamp >= cutoff)\
                .order_by(UptimeHistory.timestamp.desc())\
                .all()
    
    def get_uptime_percentage(self, url: str, days: int = 30) -> float:
        """Calculate uptime percentage for a URL."""
        history = self.get_uptime_history(url, days)
        if not history:
            return 100.0
        up_count = sum(1 for h in history if h.is_up)
        return (up_count / len(history)) * 100
    
    def get_broken_links(self, limit: int = 100) -> List[BrokenLink]:
        """Get all broken links."""
        with self.get_session() as session:
            return session.query(BrokenLink)\
                .order_by(BrokenLink.last_detected.desc())\
                .limit(limit)\
                .all()
    
    def get_performance_trends(self, url: str, days: int = 30) -> List[PerformanceMetric]:
        """Get performance metrics over time."""
        from datetime import timedelta
        with self.get_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            return session.query(PerformanceMetric)\
                .filter(PerformanceMetric.url == url)\
                .filter(PerformanceMetric.timestamp >= cutoff)\
                .order_by(PerformanceMetric.timestamp.asc())\
                .all()
    
    def cleanup_old_data(self, days: int = 90):
        """Remove data older than specified days."""
        from datetime import timedelta
        with self.get_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            session.query(UptimeHistory).filter(UptimeHistory.timestamp < cutoff).delete()
            session.query(PerformanceMetric).filter(PerformanceMetric.timestamp < cutoff).delete()
            session.query(AlertLog).filter(AlertLog.timestamp < cutoff).delete()
            
            old_checks = session.query(MonitorCheck).filter(MonitorCheck.start_time < cutoff).all()
            for check in old_checks:
                session.delete(check)
            
            session.commit()


# Singleton instance
_db_instance: Optional[Database] = None


def get_database(config: dict = None) -> Database:
    """Get the database singleton instance."""
    global _db_instance
    if _db_instance is None:
        if config:
            db_config = config.get('database', {})
            db_type = db_config.get('type', 'sqlite')
            if db_type == 'sqlite':
                _db_instance = Database(db_type='sqlite', sqlite_path=db_config.get('sqlite_path', 'data/monitor.db'))
            else:
                _db_instance = Database(db_type='mysql', **db_config.get('mysql', {}))
        else:
            _db_instance = Database()
    return _db_instance
