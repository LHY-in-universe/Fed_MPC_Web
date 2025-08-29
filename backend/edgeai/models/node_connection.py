"""
节点连接数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from models.base import db

class NodeConnection(db.Model):
    """节点连接模型"""
    __tablename__ = 'edgeai_node_connections'
    
    id = Column(Integer, primary_key=True)
    
    # 连接关系
    control_node_id = Column(Integer, ForeignKey('edgeai_control_nodes.id'), nullable=False, comment='控制节点ID')
    edge_node_id = Column(Integer, ForeignKey('edgeai_edge_nodes.id'), nullable=False, comment='边缘节点ID')
    
    # 连接状态
    status = Column(
        Enum('establishing', 'active', 'inactive', 'disconnected', 'error', name='connection_status'),
        default='establishing',
        comment='连接状态'
    )
    
    # 连接类型和优先级
    connection_type = Column(
        Enum('primary', 'secondary', 'backup', name='connection_type'),
        default='primary',
        comment='连接类型'
    )
    priority = Column(Integer, default=1, comment='连接优先级')
    
    # 网络性能指标
    latency = Column(Integer, comment='延迟(ms)')
    bandwidth = Column(Float, comment='带宽(Mbps)')
    packet_loss = Column(Float, default=0.0, comment='丢包率(%)')
    throughput = Column(Float, comment='吞吐量(Mbps)')
    
    # 连接质量评分
    quality_score = Column(Float, comment='连接质量评分(0-100)')
    stability_score = Column(Float, comment='稳定性评分(0-100)')
    
    # 流量统计
    bytes_sent = Column(Integer, default=0, comment='发送字节数')
    bytes_received = Column(Integer, default=0, comment='接收字节数')
    packets_sent = Column(Integer, default=0, comment='发送包数')
    packets_received = Column(Integer, default=0, comment='接收包数')
    
    # 连接配置
    config = Column(JSON, comment='连接配置JSON')
    encryption_enabled = Column(Text, default='true', comment='是否启用加密')
    compression_enabled = Column(Text, default='false', comment='是否启用压缩')
    
    # 错误统计
    connection_errors = Column(Integer, default=0, comment='连接错误次数')
    last_error = Column(Text, comment='最后一次错误信息')
    
    # 时间信息
    established_at = Column(DateTime, comment='连接建立时间')
    last_active = Column(DateTime, comment='最后活动时间')
    disconnected_at = Column(DateTime, comment='断开连接时间')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'control_node_id': self.control_node_id,
            'edge_node_id': self.edge_node_id,
            'status': self.status,
            'connection_type': self.connection_type,
            'priority': self.priority,
            'latency': self.latency,
            'bandwidth': self.bandwidth,
            'packet_loss': self.packet_loss,
            'throughput': self.throughput,
            'quality_score': self.quality_score,
            'stability_score': self.stability_score,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'config': self.config or {},
            'encryption_enabled': self.encryption_enabled == 'true',
            'compression_enabled': self.compression_enabled == 'true',
            'connection_errors': self.connection_errors,
            'last_error': self.last_error,
            'established_at': self.established_at.isoformat() if self.established_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'disconnected_at': self.disconnected_at.isoformat() if self.disconnected_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'control_node_name': self.control_node_ref.name if hasattr(self, 'control_node_ref') and self.control_node_ref else None,
            'edge_node_name': self.edge_node_ref.name if hasattr(self, 'edge_node_ref') and self.edge_node_ref else None,
            'is_active': self.is_active(),
            'uptime': self.get_uptime(),
            'total_bytes': self.bytes_sent + self.bytes_received
        }
    
    def establish_connection(self):
        """建立连接"""
        self.status = 'active'
        self.established_at = datetime.utcnow()
        self.last_active = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def disconnect(self, reason=None):
        """断开连接"""
        self.status = 'disconnected'
        self.disconnected_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if reason:
            self.last_error = reason
    
    def mark_error(self, error_message):
        """标记连接错误"""
        self.status = 'error'
        self.connection_errors += 1
        self.last_error = error_message
        self.updated_at = datetime.utcnow()
    
    def update_activity(self):
        """更新活动时间"""
        self.last_active = datetime.utcnow()
        if self.status == 'inactive':
            self.status = 'active'
        self.updated_at = datetime.utcnow()
    
    def update_performance_metrics(self, latency=None, bandwidth=None, packet_loss=None, throughput=None):
        """更新性能指标"""
        if latency is not None:
            self.latency = latency
        if bandwidth is not None:
            self.bandwidth = bandwidth
        if packet_loss is not None:
            self.packet_loss = packet_loss
        if throughput is not None:
            self.throughput = throughput
        
        # 计算质量评分
        self.calculate_quality_score()
        self.update_activity()
    
    def update_traffic_stats(self, bytes_sent=0, bytes_received=0, packets_sent=0, packets_received=0):
        """更新流量统计"""
        self.bytes_sent += bytes_sent
        self.bytes_received += bytes_received
        self.packets_sent += packets_sent
        self.packets_received += packets_received
        self.update_activity()
    
    def calculate_quality_score(self):
        """计算连接质量评分"""
        score = 100
        
        # 延迟影响 (延迟越低越好)
        if self.latency:
            if self.latency > 1000:  # > 1秒
                score -= 50
            elif self.latency > 500:  # > 500ms
                score -= 30
            elif self.latency > 100:  # > 100ms
                score -= 15
            elif self.latency > 50:   # > 50ms
                score -= 5
        
        # 丢包率影响
        if self.packet_loss:
            score -= min(30, self.packet_loss * 10)
        
        # 连接错误影响
        if self.connection_errors > 0:
            score -= min(20, self.connection_errors * 2)
        
        # 带宽影响 (带宽越高越好)
        if self.bandwidth:
            if self.bandwidth < 1:  # < 1Mbps
                score -= 20
            elif self.bandwidth < 10:  # < 10Mbps
                score -= 10
        
        self.quality_score = max(0, min(100, score))
    
    def calculate_stability_score(self):
        """计算稳定性评分"""
        if not self.established_at:
            self.stability_score = 0
            return
        
        # 基础稳定性评分
        score = 100
        
        # 根据连接错误次数扣分
        score -= min(50, self.connection_errors * 5)
        
        # 根据连接持续时间加分
        if self.status == 'active':
            uptime_hours = self.get_uptime() / 3600
            if uptime_hours > 24:  # 连续24小时以上
                score += 10
            elif uptime_hours > 12:  # 连续12小时以上
                score += 5
        
        self.stability_score = max(0, min(100, score))
    
    def is_active(self):
        """判断连接是否活跃"""
        if self.status != 'active':
            return False
        
        if not self.last_active:
            return False
        
        # 如果超过5分钟没有活动，认为不活跃
        threshold = datetime.utcnow() - timedelta(minutes=5)
        return self.last_active > threshold
    
    def get_uptime(self):
        """获取连接持续时间（秒）"""
        if not self.established_at:
            return 0
        
        if self.status == 'disconnected' and self.disconnected_at:
            return int((self.disconnected_at - self.established_at).total_seconds())
        elif self.status == 'active':
            return int((datetime.utcnow() - self.established_at).total_seconds())
        
        return 0
    
    def get_performance_summary(self):
        """获取性能摘要"""
        return {
            'latency': f"{self.latency}ms" if self.latency else "未知",
            'bandwidth': f"{self.bandwidth:.1f}Mbps" if self.bandwidth else "未知",
            'packet_loss': f"{self.packet_loss:.2f}%" if self.packet_loss else "0%",
            'quality_score': f"{self.quality_score:.1f}/100" if self.quality_score else "未评分",
            'stability_score': f"{self.stability_score:.1f}/100" if self.stability_score else "未评分",
            'total_traffic': self.format_bytes(self.bytes_sent + self.bytes_received),
            'uptime': self.format_uptime(self.get_uptime())
        }
    
    def format_bytes(self, bytes_count):
        """格式化字节数"""
        if bytes_count < 1024:
            return f"{bytes_count}B"
        elif bytes_count < 1024 * 1024:
            return f"{bytes_count/1024:.1f}KB"
        elif bytes_count < 1024 * 1024 * 1024:
            return f"{bytes_count/(1024*1024):.1f}MB"
        else:
            return f"{bytes_count/(1024*1024*1024):.1f}GB"
    
    def format_uptime(self, seconds):
        """格式化运行时间"""
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            return f"{seconds//60}分钟"
        elif seconds < 86400:
            return f"{seconds//3600}小时{(seconds%3600)//60}分钟"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}天{hours}小时"
    
    def __repr__(self):
        return f'<NodeConnection control:{self.control_node_id} -> edge:{self.edge_node_id} ({self.status})>'