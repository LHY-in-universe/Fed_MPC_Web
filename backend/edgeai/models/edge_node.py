"""
边缘节点数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from models.base import db

class EdgeNode(db.Model):
    """边缘节点模型"""
    __tablename__ = 'edgeai_edge_nodes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, comment='节点名称')
    node_id = Column(String(64), unique=True, nullable=False, comment='节点唯一ID')
    ip_address = Column(String(45), comment='IP地址')
    port = Column(Integer, default=8080, comment='端口号')
    
    # 项目关联
    project_id = Column(Integer, ForeignKey('edgeai_projects.id'), nullable=False, comment='所属项目ID')
    
    # 节点状态
    status = Column(
        Enum('offline', 'online', 'training', 'completed', 'error', 'idle', name='edge_node_status'),
        default='offline',
        comment='节点状态'
    )
    
    # 训练信息
    training_progress = Column(Integer, default=0, comment='训练进度(0-100)')
    current_round = Column(Integer, default=0, comment='当前训练轮次')
    total_rounds = Column(Integer, default=100, comment='总训练轮次')
    accuracy = Column(Float, comment='当前准确率')
    loss = Column(Float, comment='当前损失值')
    
    # 设备信息
    device_info = Column(JSON, comment='设备信息JSON')
    system_info = Column(JSON, comment='系统信息JSON') 
    performance_metrics = Column(JSON, comment='性能指标JSON')
    
    # 网络信息
    network_latency = Column(Integer, comment='网络延迟(ms)')
    bandwidth = Column(Float, comment='带宽(Mbps)')
    last_heartbeat = Column(DateTime, comment='最后心跳时间')
    
    # 位置信息（用于可视化）
    position_x = Column(Float, comment='X坐标')
    position_y = Column(Float, comment='Y坐标')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    connected_at = Column(DateTime, comment='连接时间')
    
    # 关系
    training_tasks = relationship('TrainingTask', backref='edge_node', cascade='all, delete-orphan')
    connections = relationship('NodeConnection', 
                             foreign_keys='NodeConnection.edge_node_id',
                             backref='edge_node_ref',
                             cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'node_id': self.node_id,
            'ip_address': self.ip_address,
            'port': self.port,
            'project_id': self.project_id,
            'status': self.status,
            'training_progress': self.training_progress,
            'current_round': self.current_round,
            'total_rounds': self.total_rounds,
            'accuracy': self.accuracy,
            'loss': self.loss,
            'device_info': self.device_info or {},
            'system_info': self.system_info or {},
            'performance_metrics': self.performance_metrics or {},
            'network_latency': self.network_latency,
            'bandwidth': self.bandwidth,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'connected_at': self.connected_at.isoformat() if self.connected_at else None,
            'is_online': self.is_online(),
            'uptime': self.get_uptime()
        }
    
    def is_online(self):
        """判断节点是否在线"""
        if not self.last_heartbeat:
            return False
        
        # 如果超过60秒没有心跳，认为离线
        threshold = datetime.utcnow() - timedelta(seconds=60)
        return self.last_heartbeat > threshold
    
    def get_uptime(self):
        """获取在线时长（秒）"""
        if not self.connected_at:
            return 0
        
        if self.status == 'offline':
            return 0
        
        return int((datetime.utcnow() - self.connected_at).total_seconds())
    
    def update_heartbeat(self):
        """更新心跳时间"""
        self.last_heartbeat = datetime.utcnow()
        if self.status == 'offline':
            self.status = 'online'
            if not self.connected_at:
                self.connected_at = datetime.utcnow()
    
    def update_training_progress(self, progress, round_num=None, accuracy=None, loss=None):
        """更新训练进度"""
        self.training_progress = min(100, max(0, progress))
        if round_num is not None:
            self.current_round = round_num
        if accuracy is not None:
            self.accuracy = accuracy
        if loss is not None:
            self.loss = loss
        
        # 根据进度更新状态
        if self.training_progress >= 100:
            self.status = 'completed'
        elif self.training_progress > 0:
            self.status = 'training'
    
    def get_device_summary(self):
        """获取设备信息摘要"""
        if not self.device_info:
            return "未知设备"
        
        cpu = self.device_info.get('cpu', {}).get('model', 'Unknown CPU')
        memory = self.device_info.get('memory', {}).get('total_gb', 0)
        gpu = self.device_info.get('gpu', {}).get('model', 'No GPU')
        
        return f"CPU: {cpu[:30]}..., RAM: {memory}GB, GPU: {gpu[:30]}..."
    
    def __repr__(self):
        return f'<EdgeNode {self.name} ({self.node_id})>'