"""
数据库初始化和管理工具
提供数据库创建、迁移、初始化数据等功能
"""

import os
import logging
from flask import Flask
from models.base import db
from models import (
    User, Project, TrainingSession, SessionParticipant,
    TrainingRound, TrainingRequest, SystemLog, SystemConfig
)
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用"""
        self.app = app
        db.init_app(app)
    
    def create_tables(self):
        """创建数据库表"""
        with self.app.app_context():
            try:
                db.create_all()
                logger.info("数据库表创建成功")
                return True
            except Exception as e:
                logger.error(f"创建数据库表失败: {str(e)}")
                return False
    
    def drop_tables(self):
        """删除数据库表"""
        with self.app.app_context():
            try:
                db.drop_all()
                logger.info("数据库表删除成功")
                return True
            except Exception as e:
                logger.error(f"删除数据库表失败: {str(e)}")
                return False
    
    def init_default_data(self):
        """初始化默认数据"""
        with self.app.app_context():
            try:
                # 创建默认管理员用户
                self._create_default_admins()
                
                # 创建系统配置
                self._create_system_config()
                
                # 创建示例项目（可选）
                self._create_demo_projects()
                
                logger.info("默认数据初始化完成")
                return True
            except Exception as e:
                logger.error(f"初始化默认数据失败: {str(e)}")
                db.session.rollback()
                return False
    
    def _create_default_admins(self):
        """创建默认管理员"""
        # AI业务管理员
        ai_admin = User.find_by_username('admin')
        if not ai_admin:
            ai_admin = User.create_user(
                username='admin',
                password='admin123',
                user_type='server',
                business_type='ai',
                full_name='AI业务管理员',
                organization='联邦学习平台',
                email='admin@federated.com'
            )
            logger.info(f"创建AI管理员: {ai_admin.username}")
        
        # 区块链业务管理员
        blockchain_admin = User.find_by_username('blockchain-admin')
        if not blockchain_admin:
            blockchain_admin = User.create_user(
                username='blockchain-admin',
                password='admin123',
                user_type='server',
                business_type='blockchain',
                full_name='区块链业务管理员',
                organization='联邦学习平台',
                email='blockchain-admin@federated.com'
            )
            logger.info(f"创建区块链管理员: {blockchain_admin.username}")
        
        # 创建示例客户端用户
        test_clients = [
            {
                'username': 'client-ai-1',
                'password': 'client123',
                'user_type': 'client',
                'business_type': 'ai',
                'full_name': 'AI客户端1',
                'organization': '上海一厂'
            },
            {
                'username': 'client-blockchain-1',
                'password': 'client123',
                'user_type': 'client',
                'business_type': 'blockchain',
                'full_name': '区块链客户端1',
                'organization': '工商银行'
            }
        ]
        
        for client_data in test_clients:
            username = client_data['username']
            if not User.find_by_username(username):
                client = User.create_user(**client_data)
                logger.info(f"创建示例客户端: {client.username}")
    
    def _create_system_config(self):
        """创建系统配置"""
        from models.system_config import SystemConfig
        
        default_configs = [
            {
                'config_key': 'platform_name',
                'config_value': '联邦学习平台',
                'description': '平台名称'
            },
            {
                'config_key': 'max_training_rounds',
                'config_value': '1000',
                'description': '最大训练轮数'
            },
            {
                'config_key': 'session_timeout',
                'config_value': '3600',
                'description': '会话超时时间（秒）'
            },
            {
                'config_key': 'heartbeat_interval',
                'config_value': '30',
                'description': '心跳间隔（秒）'
            },
            {
                'config_key': 'max_participants',
                'config_value': '100',
                'description': '最大参与方数量'
            },
            {
                'config_key': 'supported_business_types',
                'config_value': '["ai", "blockchain"]',
                'description': '支持的业务类型'
            },
            {
                'config_key': 'supported_training_modes',
                'config_value': '["normal", "mpc"]',
                'description': '支持的训练模式'
            }
        ]
        
        for config_data in default_configs:
            existing_config = SystemConfig.query.filter_by(
                config_key=config_data['config_key']
            ).first()
            
            if not existing_config:
                config = SystemConfig(**config_data)
                config.save()
                logger.info(f"创建系统配置: {config_data['config_key']}")
    
    def _create_demo_projects(self):
        """创建演示项目"""
        # 获取示例用户
        ai_client = User.find_by_username('client-ai-1')
        blockchain_client = User.find_by_username('client-blockchain-1')
        
        if ai_client:
            # AI示例项目
            ai_project = Project.create_project(
                user_id=ai_client.id,
                name='CNC机床主轴故障预测',
                project_type='local',
                training_mode='normal',
                business_type='ai',
                description='基于深度学习的CNC机床主轴故障预测模型训练',
                model_type='CNN',
                accuracy=0.895,
                current_round=45,
                total_rounds=100,
                nodes_online=1,
                nodes_total=1
            )
            ai_project.status = 'running'
            ai_project.save()
            logger.info(f"创建AI演示项目: {ai_project.name}")
        
        if blockchain_client:
            # 区块链示例项目
            blockchain_project = Project.create_project(
                user_id=blockchain_client.id,
                name='信用风险评估模型',
                project_type='local',
                training_mode='mpc',
                business_type='blockchain',
                description='基于区块链的信用风险评估联邦学习模型',
                model_type='FinNet-Risk',
                accuracy=0.923,
                current_round=32,
                total_rounds=100,
                nodes_online=1,
                nodes_total=1
            )
            blockchain_project.status = 'running'
            blockchain_project.save()
            logger.info(f"创建区块链演示项目: {blockchain_project.name}")
    
    def reset_database(self):
        """重置数据库（删除所有表并重新创建）"""
        logger.warning("开始重置数据库...")
        
        # 删除所有表
        if not self.drop_tables():
            return False
        
        # 重新创建表
        if not self.create_tables():
            return False
        
        # 初始化默认数据
        if not self.init_default_data():
            return False
        
        logger.info("数据库重置完成")
        return True

def init_database(app):
    """初始化数据库的便捷函数"""
    db_manager = DatabaseManager(app)
    
    with app.app_context():
        # 创建表
        db_manager.create_tables()
        
        # 初始化默认数据
        db_manager.init_default_data()
    
    return db_manager

# CLI命令（如果需要的话）
def create_cli_commands(app):
    """创建CLI命令"""
    
    @app.cli.command()
    def init_db():
        """初始化数据库"""
        db_manager = DatabaseManager(app)
        if db_manager.create_tables():
            print("✅ 数据库表创建成功")
        else:
            print("❌ 数据库表创建失败")
    
    @app.cli.command()
    def reset_db():
        """重置数据库"""
        db_manager = DatabaseManager(app)
        if db_manager.reset_database():
            print("✅ 数据库重置成功")
        else:
            print("❌ 数据库重置失败")
    
    @app.cli.command()
    def seed_db():
        """填充默认数据"""
        db_manager = DatabaseManager(app)
        if db_manager.init_default_data():
            print("✅ 默认数据填充成功")
        else:
            print("❌ 默认数据填充失败")