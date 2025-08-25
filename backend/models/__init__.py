"""
数据库模型模块
定义所有的SQLAlchemy模型
"""

from .user import User
from .system_log import SystemLog
from .system_config import SystemConfig

# 从AI模块导入模型
try:
    from ai.models import Project, TrainingSession, TrainingRound, TrainingRequest
    try:
        from ai.models import SessionParticipant
    except ImportError:
        # 如果不存在就创建一个简单的类
        from .base import db
        class SessionParticipant(db.Model):
            __tablename__ = 'session_participants'
            id = db.Column(db.Integer, primary_key=True)
            session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'))
            user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
except ImportError:
    # 如果AI模块导入失败，创建占位类
    from .base import db
    
    class Project(db.Model):
        __tablename__ = 'projects'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100))
    
    class TrainingSession(db.Model):
        __tablename__ = 'training_sessions'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100))
    
    class TrainingRound(db.Model):
        __tablename__ = 'training_rounds'
        id = db.Column(db.Integer, primary_key=True)
        session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'))
    
    class TrainingRequest(db.Model):
        __tablename__ = 'training_requests'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    class SessionParticipant(db.Model):
        __tablename__ = 'session_participants'
        id = db.Column(db.Integer, primary_key=True)
        session_id = db.Column(db.Integer, db.ForeignKey('training_sessions.id'))
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

__all__ = [
    'User',
    'SystemLog',
    'SystemConfig',
    'Project',
    'TrainingSession',
    'TrainingRound', 
    'TrainingRequest',
    'SessionParticipant'
]