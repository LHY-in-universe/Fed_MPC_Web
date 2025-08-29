"""
控制节点数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import db

class ControlNode(db.Model):
    """控制节点模型"""
    __tablename__ = 'edgeai_control_nodes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, comment='控制节点名称')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    project_id = Column(Integer, ForeignKey('edgeai_projects.id'), nullable=False, comment='所属项目ID')
    
    # 节点角色和权限
    role = Column(
        Enum('master', 'participant', 'observer', name='control_node_role'),
        default='participant',
        comment='节点角色'
    )
    permissions = Column(JSON, comment='权限列表JSON')
    
    # 节点状态
    status = Column(
        Enum('active', 'inactive', 'suspended', name='control_node_status'),
        default='active',
        comment='节点状态'
    )
    
    # 位置信息（用于可视化）
    position_x = Column(Integer, comment='X坐标')
    position_y = Column(Integer, comment='Y坐标')
    
    # 连接信息
    ip_address = Column(String(45), comment='IP地址')
    last_active = Column(DateTime, comment='最后活动时间')
    session_id = Column(String(128), comment='会话ID')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    user = relationship('User', backref='control_nodes')
    connections = relationship('NodeConnection',
                             foreign_keys='NodeConnection.control_node_id',
                             backref='control_node_ref',
                             cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'role': self.role,
            'permissions': self.permissions or [],
            'status': self.status,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'ip_address': self.ip_address,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_name': self.user.username if self.user else None,
            'is_master': self.role == 'master',
            'can_manage_nodes': self.has_permission('manage_nodes'),
            'can_start_training': self.has_permission('start_training')
        }
    
    def has_permission(self, permission):
        """检查是否有特定权限"""
        if self.role == 'master':
            return True
        
        if not self.permissions:
            return False
        
        return permission in self.permissions
    
    def get_default_permissions(self):
        """根据角色获取默认权限"""
        default_perms = {
            'master': [
                'manage_nodes', 'start_training', 'stop_training',
                'invite_users', 'manage_permissions', 'view_all_data',
                'export_data', 'delete_project'
            ],
            'participant': [
                'view_nodes', 'view_training', 'start_training',
                'view_own_data'
            ],
            'observer': [
                'view_nodes', 'view_training'
            ]
        }
        return default_perms.get(self.role, [])
    
    def set_default_permissions(self):
        """设置默认权限"""
        self.permissions = self.get_default_permissions()
    
    def update_activity(self):
        """更新活动时间"""
        self.last_active = datetime.utcnow()
        if self.status == 'inactive':
            self.status = 'active'
    
    def get_connected_edge_nodes(self):
        """获取连接的边缘节点"""
        return [conn.edge_node_ref for conn in self.connections if conn.edge_node_ref]
    
    def can_control_node(self, edge_node_id):
        """检查是否可以控制指定的边缘节点"""
        if self.role == 'master':
            return True
        
        # 检查是否有直接连接
        for conn in self.connections:
            if conn.edge_node_id == edge_node_id and conn.status == 'active':
                return True
        
        return False
    
    def __repr__(self):
        return f'<ControlNode {self.name} ({self.role})>'