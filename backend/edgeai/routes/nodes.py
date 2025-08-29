"""
EdgeAI节点管理路由
"""

from flask import Blueprint, request, jsonify
from models.base import db
from edgeai.models import EdgeNode, ControlNode, NodeConnection, EdgeAIProject
from datetime import datetime
from sqlalchemy import desc, and_

nodes_bp = Blueprint('nodes', __name__)

# ===== 边缘节点路由 =====

@nodes_bp.route('/edge', methods=['GET'])
def list_edge_nodes():
    """获取边缘节点列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        project_id = request.args.get('project_id', type=int)
        status = request.args.get('status', '')
        search = request.args.get('search', '')
        
        query = EdgeNode.query
        
        # 项目过滤
        if project_id:
            query = query.filter(EdgeNode.project_id == project_id)
        
        # 状态过滤
        if status:
            query = query.filter(EdgeNode.status == status)
        
        # 搜索过滤
        if search:
            query = query.filter(EdgeNode.name.contains(search))
        
        # 分页
        nodes = query.order_by(desc(EdgeNode.updated_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'nodes': [node.to_dict() for node in nodes.items],
                'total': nodes.total,
                'pages': nodes.pages,
                'current_page': page,
                'has_next': nodes.has_next,
                'has_prev': nodes.has_prev
            }
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取边缘节点列表失败: {str(e)}'
        }), 500

@nodes_bp.route('/edge', methods=['POST'])
def create_edge_node():
    """创建边缘节点"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'node_id', 'project_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 检查项目是否存在
        project = EdgeAIProject.query.get(data['project_id'])
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404
        
        # 检查node_id是否唯一
        existing_node = EdgeNode.query.filter_by(node_id=data['node_id']).first()
        if existing_node:
            return jsonify({
                'code': 400,
                'message': '节点ID已存在'
            }), 400
        
        # 创建节点
        node = EdgeNode(
            name=data['name'],
            node_id=data['node_id'],
            project_id=data['project_id'],
            ip_address=data.get('ip_address'),
            port=data.get('port', 8080),
            device_info=data.get('device_info', {}),
            system_info=data.get('system_info', {}),
            position_x=data.get('position_x'),
            position_y=data.get('position_y')
        )
        
        db.session.add(node)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '边缘节点创建成功',
            'data': node.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建边缘节点失败: {str(e)}'
        }), 500

@nodes_bp.route('/edge/<int:node_id>', methods=['GET'])
def get_edge_node(node_id):
    """获取边缘节点详情"""
    try:
        node = EdgeNode.query.get_or_404(node_id)
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': node.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取边缘节点详情失败: {str(e)}'
        }), 500

@nodes_bp.route('/edge/<int:node_id>', methods=['PUT'])
def update_edge_node(node_id):
    """更新边缘节点"""
    try:
        node = EdgeNode.query.get_or_404(node_id)
        data = request.get_json()
        
        # 更新字段
        updatable_fields = ['name', 'ip_address', 'port', 'status', 'device_info', 
                          'system_info', 'position_x', 'position_y']
        
        for field in updatable_fields:
            if field in data:
                setattr(node, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '边缘节点更新成功',
            'data': node.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新边缘节点失败: {str(e)}'
        }), 500

@nodes_bp.route('/edge/<int:node_id>/heartbeat', methods=['POST'])
def update_edge_node_heartbeat(node_id):
    """更新边缘节点心跳"""
    try:
        node = EdgeNode.query.get_or_404(node_id)
        data = request.get_json() or {}
        
        # 更新心跳
        node.update_heartbeat()
        
        # 更新性能指标
        if 'performance_metrics' in data:
            node.performance_metrics = data['performance_metrics']
        
        # 更新网络信息
        if 'network_latency' in data:
            node.network_latency = data['network_latency']
        if 'bandwidth' in data:
            node.bandwidth = data['bandwidth']
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '心跳更新成功',
            'data': {
                'node_id': node.id,
                'status': node.status,
                'is_online': node.is_online()
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新心跳失败: {str(e)}'
        }), 500

@nodes_bp.route('/edge/<int:node_id>/training', methods=['POST'])
def update_edge_node_training(node_id):
    """更新边缘节点训练进度"""
    try:
        node = EdgeNode.query.get_or_404(node_id)
        data = request.get_json()
        
        # 验证必填字段
        if 'progress' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少训练进度数据'
            }), 400
        
        # 更新训练进度
        node.update_training_progress(
            progress=data['progress'],
            round_num=data.get('current_round'),
            accuracy=data.get('accuracy'),
            loss=data.get('loss')
        )
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '训练进度更新成功',
            'data': {
                'node_id': node.id,
                'training_progress': node.training_progress,
                'current_round': node.current_round,
                'accuracy': node.accuracy,
                'loss': node.loss,
                'status': node.status
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新训练进度失败: {str(e)}'
        }), 500

# ===== 控制节点路由 =====

@nodes_bp.route('/control', methods=['GET'])
def list_control_nodes():
    """获取控制节点列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        project_id = request.args.get('project_id', type=int)
        role = request.args.get('role', '')
        
        query = ControlNode.query
        
        # 项目过滤
        if project_id:
            query = query.filter(ControlNode.project_id == project_id)
        
        # 角色过滤
        if role:
            query = query.filter(ControlNode.role == role)
        
        # 分页
        nodes = query.order_by(desc(ControlNode.updated_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'nodes': [node.to_dict() for node in nodes.items],
                'total': nodes.total,
                'pages': nodes.pages,
                'current_page': page,
                'has_next': nodes.has_next,
                'has_prev': nodes.has_prev
            }
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取控制节点列表失败: {str(e)}'
        }), 500

@nodes_bp.route('/control', methods=['POST'])
def create_control_node():
    """创建控制节点"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'user_id', 'project_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 检查项目是否存在
        project = EdgeAIProject.query.get(data['project_id'])
        if not project:
            return jsonify({
                'code': 404,
                'message': '项目不存在'
            }), 404
        
        # 创建控制节点
        node = ControlNode(
            name=data['name'],
            user_id=data['user_id'],
            project_id=data['project_id'],
            role=data.get('role', 'participant'),
            position_x=data.get('position_x'),
            position_y=data.get('position_y'),
            ip_address=data.get('ip_address')
        )
        
        # 设置默认权限
        node.set_default_permissions()
        
        db.session.add(node)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '控制节点创建成功',
            'data': node.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建控制节点失败: {str(e)}'
        }), 500

# ===== 节点连接路由 =====

@nodes_bp.route('/connections', methods=['GET'])
def list_node_connections():
    """获取节点连接列表"""
    try:
        project_id = request.args.get('project_id', type=int)
        control_node_id = request.args.get('control_node_id', type=int)
        edge_node_id = request.args.get('edge_node_id', type=int)
        status = request.args.get('status', '')
        
        query = NodeConnection.query
        
        # 过滤条件
        if project_id:
            query = query.join(ControlNode).filter(ControlNode.project_id == project_id)
        if control_node_id:
            query = query.filter(NodeConnection.control_node_id == control_node_id)
        if edge_node_id:
            query = query.filter(NodeConnection.edge_node_id == edge_node_id)
        if status:
            query = query.filter(NodeConnection.status == status)
        
        connections = query.order_by(desc(NodeConnection.updated_at)).all()
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': [conn.to_dict() for conn in connections]
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取节点连接列表失败: {str(e)}'
        }), 500

@nodes_bp.route('/connections', methods=['POST'])
def create_node_connection():
    """创建节点连接"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['control_node_id', 'edge_node_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 检查节点是否存在
        control_node = ControlNode.query.get(data['control_node_id'])
        edge_node = EdgeNode.query.get(data['edge_node_id'])
        
        if not control_node:
            return jsonify({
                'code': 404,
                'message': '控制节点不存在'
            }), 404
        
        if not edge_node:
            return jsonify({
                'code': 404,
                'message': '边缘节点不存在'
            }), 404
        
        # 检查是否已存在连接
        existing_conn = NodeConnection.query.filter(
            and_(
                NodeConnection.control_node_id == data['control_node_id'],
                NodeConnection.edge_node_id == data['edge_node_id']
            )
        ).first()
        
        if existing_conn:
            return jsonify({
                'code': 400,
                'message': '节点连接已存在'
            }), 400
        
        # 创建连接
        connection = NodeConnection(
            control_node_id=data['control_node_id'],
            edge_node_id=data['edge_node_id'],
            connection_type=data.get('connection_type', 'primary'),
            priority=data.get('priority', 1),
            config=data.get('config', {})
        )
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '节点连接创建成功',
            'data': connection.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建节点连接失败: {str(e)}'
        }), 500

@nodes_bp.route('/connections/<int:connection_id>/metrics', methods=['POST'])
def update_connection_metrics(connection_id):
    """更新连接性能指标"""
    try:
        connection = NodeConnection.query.get_or_404(connection_id)
        data = request.get_json()
        
        # 更新性能指标
        connection.update_performance_metrics(
            latency=data.get('latency'),
            bandwidth=data.get('bandwidth'),
            packet_loss=data.get('packet_loss'),
            throughput=data.get('throughput')
        )
        
        # 更新流量统计
        if any(key in data for key in ['bytes_sent', 'bytes_received', 'packets_sent', 'packets_received']):
            connection.update_traffic_stats(
                bytes_sent=data.get('bytes_sent', 0),
                bytes_received=data.get('bytes_received', 0),
                packets_sent=data.get('packets_sent', 0),
                packets_received=data.get('packets_received', 0)
            )
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '连接指标更新成功',
            'data': connection.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新连接指标失败: {str(e)}'
        }), 500