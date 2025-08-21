"""
总服务器相关路由
处理客户端管理、训练申请审批、全局监控等功能
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from routes.client import MOCK_TRAINING_REQUESTS  # 共享训练申请数据

server_bp = Blueprint('server', __name__)

# 模拟数据
MOCK_GLOBAL_PROJECTS = []
MOCK_MODELS = []
MOCK_CLIENTS = {}

@server_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """
    获取管理员仪表盘数据
    """
    try:
        business_type = request.args.get('business_type', 'ai')
        
        # 根据业务类型返回不同的模拟数据
        if business_type == 'ai':
            clients = [
                {'id': 1, 'name': '上海一厂', 'address': 'http://shanghai.client.com', 'status': 'online', 'lastSeen': '2分钟前', 'projects': 2},
                {'id': 2, 'name': '武汉二厂', 'address': 'http://wuhan.client.com', 'status': 'online', 'lastSeen': '5分钟前', 'projects': 1},
                {'id': 3, 'name': '西安三厂', 'address': 'http://xian.client.com', 'status': 'offline', 'lastSeen': '2小时前', 'projects': 1},
                {'id': 4, 'name': '广州四厂', 'address': 'http://guangzhou.client.com', 'status': 'online', 'lastSeen': '1分钟前', 'projects': 3}
            ]
            
            global_projects = [
                {
                    'id': 1,
                    'name': 'CNC机床故障预测联邦训练',
                    'participants': ['上海一厂', '武汉二厂', '广州四厂'],
                    'status': 'running',
                    'accuracy': 91.2,
                    'round': 67,
                    'totalRounds': 100
                }
            ]
            
            models = [
                {'id': 1, 'name': 'ResNet-50', 'type': 'CNN', 'size': '102MB', 'version': 'v2.1', 'downloads': 15},
                {'id': 2, 'name': 'BERT-Base', 'type': 'Transformer', 'size': '440MB', 'version': 'v1.1', 'downloads': 8},
                {'id': 3, 'name': 'YOLOv5', 'type': 'Detection', 'size': '28MB', 'version': 'v6.0', 'downloads': 23}
            ]
        else:  # blockchain
            clients = [
                {'id': 1, 'name': '工商银行', 'address': 'http://icbc.bank.com', 'status': 'online', 'lastSeen': '1分钟前', 'projects': 2},
                {'id': 2, 'name': '建设银行', 'address': 'http://ccb.bank.com', 'status': 'online', 'lastSeen': '3分钟前', 'projects': 1},
                {'id': 3, 'name': '招商银行', 'address': 'http://cmb.bank.com', 'status': 'online', 'lastSeen': '2分钟前', 'projects': 1}
            ]
            
            global_projects = [
                {
                    'id': 1,
                    'name': '银行联合风控模型训练',
                    'participants': ['工商银行', '建设银行'],
                    'status': 'running',
                    'accuracy': 94.8,
                    'round': 32,
                    'totalRounds': 50
                }
            ]
            
            models = [
                {'id': 1, 'name': 'FinNet-Risk', 'type': 'Risk Assessment', 'size': '85MB', 'version': 'v1.3', 'downloads': 12},
                {'id': 2, 'name': 'AML-Detector', 'type': 'Anti Money Laundering', 'size': '156MB', 'version': 'v2.0', 'downloads': 6},
                {'id': 3, 'name': 'Credit-Score', 'type': 'Credit Scoring', 'size': '42MB', 'version': 'v1.8', 'downloads': 18}
            ]
        
        online_clients = len([c for c in clients if c['status'] == 'online'])
        pending_requests = len([r for r in MOCK_TRAINING_REQUESTS if r['status'] == 'pending'])
        active_projects = len([p for p in global_projects if p['status'] == 'running'])
        
        return jsonify({
            'success': True,
            'stats': {
                'onlineClients': online_clients,
                'totalClients': len(clients),
                'pendingRequests': pending_requests,
                'activeProjects': active_projects,
                'availableModels': len(models)
            },
            'clients': clients,
            'globalProjects': global_projects,
            'models': models,
            'trainingRequests': MOCK_TRAINING_REQUESTS
        }), 200
        
    except Exception as e:
        logging.error(f'获取仪表盘数据错误: {str(e)}')
        return jsonify({'error': '获取仪表盘数据失败'}), 500

@server_bp.route('/clients', methods=['GET'])
def get_clients():
    """
    获取所有客户端列表
    """
    try:
        # 返回模拟客户端数据
        clients = [
            {
                'id': 1,
                'name': '上海一厂',
                'address': 'http://shanghai.client.com',
                'status': 'online',
                'lastSeen': '2分钟前',
                'projects': 2,
                'permissions': 'normal',
                'registeredAt': '2024-01-10 09:00:00'
            },
            {
                'id': 2,
                'name': '武汉二厂',
                'address': 'http://wuhan.client.com',
                'status': 'online',
                'lastSeen': '5分钟前',
                'projects': 1,
                'permissions': 'normal',
                'registeredAt': '2024-01-11 14:30:00'
            }
        ]
        
        return jsonify({
            'success': True,
            'clients': clients
        }), 200
        
    except Exception as e:
        logging.error(f'获取客户端列表错误: {str(e)}')
        return jsonify({'error': '获取客户端列表失败'}), 500

@server_bp.route('/clients', methods=['POST'])
def add_client():
    """
    添加新客户端
    """
    try:
        data = request.get_json()
        
        name = data.get('name')
        address = data.get('address')
        
        if not name or not address:
            return jsonify({'error': '客户端名称和地址不能为空'}), 400
        
        new_client = {
            'id': len(MOCK_CLIENTS) + 10,
            'name': name,
            'address': address,
            'status': 'offline',
            'lastSeen': '从未连接',
            'projects': 0,
            'permissions': 'normal',
            'registeredAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        MOCK_CLIENTS[name] = new_client
        
        logging.info(f'客户端添加成功: {name}')
        
        return jsonify({
            'success': True,
            'client': new_client
        }), 201
        
    except Exception as e:
        logging.error(f'添加客户端错误: {str(e)}')
        return jsonify({'error': '添加客户端失败'}), 500

@server_bp.route('/clients/<int:client_id>', methods=['PUT'])
def update_client():
    """
    更新客户端信息
    """
    try:
        data = request.get_json()
        
        # TODO: 实现客户端信息更新逻辑
        
        return jsonify({
            'success': True,
            'message': '客户端信息更新成功'
        }), 200
        
    except Exception as e:
        logging.error(f'更新客户端错误: {str(e)}')
        return jsonify({'error': '更新客户端失败'}), 500

@server_bp.route('/clients/<int:client_id>', methods=['DELETE'])
def delete_client():
    """
    删除客户端
    """
    try:
        # TODO: 实现客户端删除逻辑
        
        return jsonify({
            'success': True,
            'message': '客户端删除成功'
        }), 200
        
    except Exception as e:
        logging.error(f'删除客户端错误: {str(e)}')
        return jsonify({'error': '删除客户端失败'}), 500

@server_bp.route('/training-requests/<int:request_id>/approve', methods=['POST'])
def approve_training_request():
    """
    批准训练申请
    """
    try:
        # 查找申请
        request_found = False
        for request_item in MOCK_TRAINING_REQUESTS:
            if request_item['id'] == request_id:
                request_item['status'] = 'approved'
                request_item['approvedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                request_found = True
                
                # 创建全局项目
                global_project = {
                    'id': len(MOCK_GLOBAL_PROJECTS) + 1,
                    'name': request_item['projectName'],
                    'participants': [request_item['clientName']],
                    'status': 'starting',
                    'accuracy': 0.0,
                    'round': 0,
                    'totalRounds': 100,
                    'createdAt': datetime.now().isoformat()
                }
                MOCK_GLOBAL_PROJECTS.append(global_project)
                break
        
        if not request_found:
            return jsonify({'error': '训练申请不存在'}), 404
        
        logging.info(f'训练申请批准成功: {request_id}')
        
        return jsonify({
            'success': True,
            'message': '训练申请已批准'
        }), 200
        
    except Exception as e:
        logging.error(f'批准训练申请错误: {str(e)}')
        return jsonify({'error': '批准训练申请失败'}), 500

@server_bp.route('/training-requests/<int:request_id>/reject', methods=['POST'])
def reject_training_request():
    """
    拒绝训练申请
    """
    try:
        data = request.get_json()
        reason = data.get('reason', '未提供拒绝原因')
        
        # 查找并拒绝申请
        request_found = False
        for request_item in MOCK_TRAINING_REQUESTS:
            if request_item['id'] == request_id:
                request_item['status'] = 'rejected'
                request_item['rejectedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                request_item['rejectionReason'] = reason
                request_found = True
                break
        
        if not request_found:
            return jsonify({'error': '训练申请不存在'}), 404
        
        logging.info(f'训练申请拒绝: {request_id}，原因: {reason}')
        
        return jsonify({
            'success': True,
            'message': '训练申请已拒绝'
        }), 200
        
    except Exception as e:
        logging.error(f'拒绝训练申请错误: {str(e)}')
        return jsonify({'error': '拒绝训练申请失败'}), 500

@server_bp.route('/models', methods=['GET'])
def get_models():
    """
    获取模型列表
    """
    try:
        business_type = request.args.get('business_type', 'ai')
        
        if business_type == 'ai':
            models = [
                {'id': 1, 'name': 'ResNet-50', 'type': 'CNN', 'size': '102MB', 'version': 'v2.1', 'downloads': 15, 'uploadedAt': '2024-01-10'},
                {'id': 2, 'name': 'BERT-Base', 'type': 'Transformer', 'size': '440MB', 'version': 'v1.1', 'downloads': 8, 'uploadedAt': '2024-01-12'},
                {'id': 3, 'name': 'YOLOv5', 'type': 'Detection', 'size': '28MB', 'version': 'v6.0', 'downloads': 23, 'uploadedAt': '2024-01-08'}
            ]
        else:
            models = [
                {'id': 1, 'name': 'FinNet-Risk', 'type': 'Risk Assessment', 'size': '85MB', 'version': 'v1.3', 'downloads': 12, 'uploadedAt': '2024-01-09'},
                {'id': 2, 'name': 'AML-Detector', 'type': 'Anti Money Laundering', 'size': '156MB', 'version': 'v2.0', 'downloads': 6, 'uploadedAt': '2024-01-11'},
                {'id': 3, 'name': 'Credit-Score', 'type': 'Credit Scoring', 'size': '42MB', 'version': 'v1.8', 'downloads': 18, 'uploadedAt': '2024-01-07'}
            ]
        
        return jsonify({
            'success': True,
            'models': models
        }), 200
        
    except Exception as e:
        logging.error(f'获取模型列表错误: {str(e)}')
        return jsonify({'error': '获取模型列表失败'}), 500

@server_bp.route('/models', methods=['POST'])
def upload_model():
    """
    上传模型文件
    TODO: 实现文件上传逻辑
    """
    return jsonify({
        'error': '模型上传功能暂未实现',
        'message': '请使用文件管理系统上传模型'
    }), 501

@server_bp.route('/models/<int:model_id>/download', methods=['GET'])
def download_model():
    """
    下载模型文件
    TODO: 实现文件下载逻辑
    """
    return jsonify({
        'success': True,
        'downloadUrl': f'/downloads/model_{model_id}.zip',
        'message': '模型下载链接已生成'
    }), 200

@server_bp.route('/system/config', methods=['GET'])
def get_system_config():
    """
    获取系统配置信息
    """
    try:
        config = {
            'maxTrainingRounds': 1000,
            'supportedBusinessTypes': ['ai', 'blockchain'],
            'supportedTrainingModes': ['normal', 'mpc'],
            'maxClientConnections': 100,
            'defaultModelPath': '/models/',
            'logLevel': 'INFO'
        }
        
        return jsonify({
            'success': True,
            'config': config
        }), 200
        
    except Exception as e:
        logging.error(f'获取系统配置错误: {str(e)}')
        return jsonify({'error': '获取系统配置失败'}), 500

@server_bp.route('/system/config', methods=['PUT'])
def update_system_config():
    """
    更新系统配置
    TODO: 实现配置更新逻辑
    """
    return jsonify({
        'success': True,
        'message': '系统配置更新成功'
    }), 200