"""
用户服务
提供用户相关的业务逻辑操作
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.base import db


class UserService:
    """用户服务类"""
    
    @staticmethod
    def create_user(username, password, user_type, business_type, full_name, email, organization=''):
        """创建用户"""
        try:
            # 检查用户是否已存在
            if User.query.filter_by(username=username).first():
                return None
            
            # 创建新用户
            user = User(
                username=username,
                password_hash=generate_password_hash(password),
                user_type=user_type,
                business_type=business_type,
                full_name=full_name,
                email=email,
                organization=organization,
                status='active'
            )
            
            db.session.add(user)
            db.session.commit()
            
            return user
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def authenticate_user(username, password):
        """验证用户身份"""
        try:
            user = User.query.filter_by(username=username, status='active').first()
            
            if user and check_password_hash(user.password_hash, password):
                return user
            
            return None
        except Exception as e:
            raise e
    
    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户"""
        try:
            return User.query.filter_by(id=user_id).first()
        except Exception as e:
            raise e
    
    @staticmethod
    def get_user_by_username(username):
        """根据用户名获取用户"""
        try:
            return User.query.filter_by(username=username).first()
        except Exception as e:
            raise e
    
    @staticmethod
    def update_last_login(user_id):
        """更新用户最后登录时间"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if user:
                user.last_login = datetime.now()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def update_user_profile(user_id, **kwargs):
        """更新用户资料"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return None
            
            # 更新允许的字段
            allowed_fields = ['full_name', 'email', 'organization']
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(user, field, value)
            
            user.updated_at = datetime.now()
            db.session.commit()
            
            return user
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """修改密码"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return False, "用户不存在"
            
            # 验证旧密码
            if not check_password_hash(user.password_hash, old_password):
                return False, "旧密码不正确"
            
            # 设置新密码
            user.password_hash = generate_password_hash(new_password)
            user.updated_at = datetime.now()
            db.session.commit()
            
            return True, "密码修改成功"
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def deactivate_user(user_id):
        """停用用户"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if user:
                user.status = 'inactive'
                user.updated_at = datetime.now()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_users_by_business_type(business_type, user_type=None):
        """根据业务类型获取用户列表"""
        try:
            query = User.query.filter_by(business_type=business_type, status='active')
            
            if user_type:
                query = query.filter_by(user_type=user_type)
            
            return query.all()
        except Exception as e:
            raise e
    
    @staticmethod
    def get_user_stats():
        """获取用户统计信息"""
        try:
            stats = {
                'total_users': User.query.count(),
                'active_users': User.query.filter_by(status='active').count(),
                'by_business_type': {},
                'by_user_type': {}
            }
            
            # 按业务类型统计
            for business_type in ['homepage', 'ai', 'blockchain', 'crypto']:
                count = User.query.filter_by(business_type=business_type, status='active').count()
                stats['by_business_type'][business_type] = count
            
            # 按用户类型统计
            for user_type in ['client', 'server']:
                count = User.query.filter_by(user_type=user_type, status='active').count()
                stats['by_user_type'][user_type] = count
            
            return stats
        except Exception as e:
            raise e