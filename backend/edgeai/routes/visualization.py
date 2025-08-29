"""
EdgeAI可视化数据路由
"""

from flask import Blueprint, request, jsonify
from models.base import db
from edgeai.models import EdgeNode, ControlNode, NodeConnection, EdgeAIProject, TrainingTask
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_

visualization_bp = Blueprint('visualization', __name__)

@visualization_bp.route('/network/<int:project_id>', methods=['GET'])
def get_network_topology(project_id):
    """获取网络拓扑数据"""
    try:
        project = EdgeAIProject.query.get_or_404(project_id)
        
        # 获取控制节点
        control_nodes = ControlNode.query.filter_by(project_id=project_id).all()
        
        # 获取边缘节点
        edge_nodes = EdgeNode.query.filter_by(project_id=project_id).all()
        
        # 获取节点连接
        connections = NodeConnection.query.join(ControlNode).filter(
            ControlNode.project_id == project_id
        ).all()
        
        # 格式化数据
        topology_data = {
            'project': {
                'id': project.id,
                'name': project.name,
                'status': project.status,
                'statistics': project.get_statistics()
            },
            'control_nodes': [
                {
                    'id': node.id,
                    'name': node.name,
                    'role': node.role,
                    'status': node.status,
                    'position': {
                        'x': node.position_x or 200 + (i * 200),
                        'y': node.position_y or 100
                    },
                    'user_name': node.user.username if node.user else None,
                    'permissions': node.permissions or [],
                    'ip_address': node.ip_address,
                    'last_active': node.last_active.isoformat() if node.last_active else None
                }
                for i, node in enumerate(control_nodes)
            ],
            'edge_nodes': [
                {
                    'id': node.id,
                    'name': node.name,
                    'node_id': node.node_id,
                    'status': node.status,
                    'position': {
                        'x': node.position_x or 100 + (i * 150),
                        'y': node.position_y or 400
                    },
                    'training_progress': node.training_progress,
                    'current_round': node.current_round,
                    'total_rounds': node.total_rounds,
                    'accuracy': node.accuracy,
                    'loss': node.loss,
                    'device_info': node.device_info or {},
                    'performance_metrics': node.performance_metrics or {},
                    'is_online': node.is_online(),
                    'uptime': node.get_uptime(),
                    'ip_address': node.ip_address,
                    'last_heartbeat': node.last_heartbeat.isoformat() if node.last_heartbeat else None
                }
                for i, node in enumerate(edge_nodes)
            ],
            'connections': [
                {
                    'id': conn.id,
                    'control_node_id': conn.control_node_id,
                    'edge_node_id': conn.edge_node_id,
                    'status': conn.status,
                    'connection_type': conn.connection_type,
                    'quality_score': conn.quality_score,
                    'latency': conn.latency,
                    'bandwidth': conn.bandwidth,
                    'packet_loss': conn.packet_loss,
                    'is_active': conn.is_active()
                }
                for conn in connections
            ]
        }
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': topology_data
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取网络拓扑失败: {str(e)}'
        }), 500

@visualization_bp.route('/training-progress/<int:project_id>', methods=['GET'])
def get_training_progress(project_id):
    """获取训练进度数据"""
    try:
        project = EdgeAIProject.query.get_or_404(project_id)
        
        # 获取边缘节点训练进度
        edge_nodes = EdgeNode.query.filter_by(project_id=project_id).all()
        
        # 计算整体进度
        total_progress = sum(node.training_progress for node in edge_nodes)
        avg_progress = total_progress / len(edge_nodes) if edge_nodes else 0
        
        # 按状态分组统计
        status_stats = {}
        for node in edge_nodes:
            status = node.status
            if status not in status_stats:
                status_stats[status] = {'count': 0, 'progress': 0}
            status_stats[status]['count'] += 1
            status_stats[status]['progress'] += node.training_progress
        
        # 计算平均指标
        avg_accuracy = sum(node.accuracy for node in edge_nodes if node.accuracy) / len([node for node in edge_nodes if node.accuracy]) if any(node.accuracy for node in edge_nodes) else 0
        avg_loss = sum(node.loss for node in edge_nodes if node.loss) / len([node for node in edge_nodes if node.loss]) if any(node.loss for node in edge_nodes) else 0
        
        progress_data = {
            'project_id': project_id,
            'project_status': project.status,
            'overall_progress': {
                'total_nodes': len(edge_nodes),
                'average_progress': round(avg_progress, 2),
                'total_progress': total_progress,
                'average_accuracy': round(avg_accuracy, 4) if avg_accuracy else None,
                'average_loss': round(avg_loss, 6) if avg_loss else None,
                'completed_nodes': len([node for node in edge_nodes if node.training_progress >= 100]),
                'active_nodes': len([node for node in edge_nodes if node.status == 'training']),
                'online_nodes': len([node for node in edge_nodes if node.is_online()])
            },
            'status_distribution': [
                {
                    'status': status,
                    'count': stats['count'],
                    'average_progress': round(stats['progress'] / stats['count'], 2)
                }
                for status, stats in status_stats.items()
            ],
            'node_progress': [
                {
                    'node_id': node.id,
                    'node_name': node.name,
                    'progress': node.training_progress,
                    'current_round': node.current_round,
                    'total_rounds': node.total_rounds,
                    'accuracy': node.accuracy,
                    'loss': node.loss,
                    'status': node.status,
                    'is_online': node.is_online()
                }
                for node in edge_nodes
            ]
        }
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': progress_data
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取训练进度失败: {str(e)}'
        }), 500

@visualization_bp.route('/real-time/<int:project_id>', methods=['GET'])
def get_real_time_data(project_id):
    """获取实时数据"""
    try:
        # 获取最近1小时的数据
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        # 获取边缘节点状态变化
        edge_nodes = EdgeNode.query.filter(
            and_(
                EdgeNode.project_id == project_id,
                EdgeNode.updated_at >= one_hour_ago
            )
        ).order_by(desc(EdgeNode.updated_at)).all()
        
        # 获取连接质量数据
        connections = NodeConnection.query.join(ControlNode).filter(
            and_(
                ControlNode.project_id == project_id,
                NodeConnection.updated_at >= one_hour_ago
            )
        ).order_by(desc(NodeConnection.updated_at)).all()
        
        # 构建实时数据
        real_time_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'project_id': project_id,
            'node_updates': [
                {
                    'node_id': node.id,
                    'node_name': node.name,
                    'status': node.status,
                    'training_progress': node.training_progress,
                    'accuracy': node.accuracy,
                    'loss': node.loss,
                    'is_online': node.is_online(),
                    'performance_metrics': node.performance_metrics or {},
                    'last_update': node.updated_at.isoformat()
                }
                for node in edge_nodes[:20]  # 限制数量
            ],
            'connection_updates': [
                {
                    'connection_id': conn.id,
                    'control_node_id': conn.control_node_id,
                    'edge_node_id': conn.edge_node_id,
                    'status': conn.status,
                    'quality_score': conn.quality_score,
                    'latency': conn.latency,
                    'bandwidth': conn.bandwidth,
                    'is_active': conn.is_active(),
                    'last_update': conn.updated_at.isoformat()
                }
                for conn in connections[:10]  # 限制数量
            ],
            'system_metrics': {
                'total_nodes_online': len([node for node in edge_nodes if node.is_online()]),
                'total_nodes_training': len([node for node in edge_nodes if node.status == 'training']),
                'total_connections_active': len([conn for conn in connections if conn.is_active()]),
                'average_latency': sum(conn.latency for conn in connections if conn.latency) / len([conn for conn in connections if conn.latency]) if any(conn.latency for conn in connections) else 0
            }
        }
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': real_time_data
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取实时数据失败: {str(e)}'
        }), 500

@visualization_bp.route('/statistics/<int:project_id>', methods=['GET'])
def get_project_statistics(project_id):
    """获取项目统计数据"""
    try:
        project = EdgeAIProject.query.get_or_404(project_id)
        
        # 基础统计
        basic_stats = project.get_statistics()
        
        # 性能统计
        edge_nodes = EdgeNode.query.filter_by(project_id=project_id).all()
        connections = NodeConnection.query.join(ControlNode).filter(
            ControlNode.project_id == project_id
        ).all()
        
        # 训练任务统计
        training_tasks = TrainingTask.query.filter_by(project_id=project_id).all()
        task_stats = {
            'total_tasks': len(training_tasks),
            'running_tasks': len([task for task in training_tasks if task.status == 'running']),
            'completed_tasks': len([task for task in training_tasks if task.status == 'completed']),
            'failed_tasks': len([task for task in training_tasks if task.status == 'failed'])
        }
        
        # 设备类型统计
        device_types = {}
        for node in edge_nodes:
            if node.device_info and 'device_type' in node.device_info:
                device_type = node.device_info['device_type']
                device_types[device_type] = device_types.get(device_type, 0) + 1
        
        # 网络性能统计
        network_stats = {
            'total_connections': len(connections),
            'active_connections': len([conn for conn in connections if conn.is_active()]),
            'average_latency': sum(conn.latency for conn in connections if conn.latency) / len([conn for conn in connections if conn.latency]) if any(conn.latency for conn in connections) else 0,
            'average_bandwidth': sum(conn.bandwidth for conn in connections if conn.bandwidth) / len([conn for conn in connections if conn.bandwidth]) if any(conn.bandwidth for conn in connections) else 0,
            'total_data_transferred': sum(conn.bytes_sent + conn.bytes_received for conn in connections)
        }
        
        # 时间线数据（最近7天）
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_nodes = EdgeNode.query.filter(
            and_(
                EdgeNode.project_id == project_id,
                EdgeNode.created_at >= seven_days_ago
            )
        ).order_by(EdgeNode.created_at).all()
        
        timeline_data = []
        current_date = seven_days_ago.date()
        end_date = datetime.utcnow().date()
        
        while current_date <= end_date:
            day_nodes = [node for node in recent_nodes if node.created_at.date() == current_date]
            timeline_data.append({
                'date': current_date.isoformat(),
                'nodes_added': len(day_nodes),
                'nodes_online': len([node for node in day_nodes if node.is_online()])
            })
            current_date += timedelta(days=1)
        
        statistics_data = {
            'project_info': {
                'id': project.id,
                'name': project.name,
                'status': project.status,
                'created_at': project.created_at.isoformat(),
                'owner_name': project.owner.username if project.owner else None
            },
            'basic_statistics': basic_stats,
            'task_statistics': task_stats,
            'network_statistics': network_stats,
            'device_distribution': [
                {'device_type': device_type, 'count': count}
                for device_type, count in device_types.items()
            ],
            'timeline': timeline_data,
            'top_performing_nodes': [
                {
                    'node_id': node.id,
                    'node_name': node.name,
                    'accuracy': node.accuracy,
                    'progress': node.training_progress
                }
                for node in sorted(edge_nodes, key=lambda x: x.accuracy or 0, reverse=True)[:5]
            ]
        }
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': statistics_data
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取项目统计失败: {str(e)}'
        }), 500

@visualization_bp.route('/node-details/<int:node_id>', methods=['GET'])
def get_node_details(node_id):
    """获取节点详细信息"""
    try:
        # 尝试作为边缘节点查找
        edge_node = EdgeNode.query.get(node_id)
        if edge_node:
            # 获取该节点的连接信息
            connections = NodeConnection.query.filter_by(edge_node_id=node_id).all()
            
            # 获取训练任务
            training_tasks = TrainingTask.query.filter_by(edge_node_id=node_id).order_by(desc(TrainingTask.created_at)).limit(5).all()
            
            node_details = {
                'type': 'edge_node',
                'node_info': edge_node.to_dict(),
                'connections': [conn.to_dict() for conn in connections],
                'training_tasks': [task.to_dict() for task in training_tasks],
                'device_summary': edge_node.get_device_summary(),
                'performance_history': []  # 可以后续添加历史性能数据
            }
            
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': node_details
            })
        
        # 尝试作为控制节点查找
        control_node = ControlNode.query.get(node_id)
        if control_node:
            # 获取该控制节点管理的连接
            connections = NodeConnection.query.filter_by(control_node_id=node_id).all()
            
            node_details = {
                'type': 'control_node',
                'node_info': control_node.to_dict(),
                'managed_connections': [conn.to_dict() for conn in connections],
                'connected_edge_nodes': [conn.edge_node_ref.to_dict() if conn.edge_node_ref else None for conn in connections],
                'permissions': control_node.permissions or [],
                'default_permissions': control_node.get_default_permissions()
            }
            
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': node_details
            })
        
        return jsonify({
            'code': 404,
            'message': '节点不存在'
        }), 404
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取节点详情失败: {str(e)}'
        }), 500