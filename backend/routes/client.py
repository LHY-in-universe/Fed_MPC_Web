"""
客户端相关路由
处理客户端项目管理、训练申请等功能
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
import json

client_bp = Blueprint('client', __name__)

# 模拟数据存储
MOCK_PROJECTS = {}
MOCK_TRAINING_REQUESTS = []

@client_bp.route('/projects', methods=['GET'])
def get_projects():
    """
    获取客户端项目列表
    
    查询参数:
    - user_id: 用户ID
    - business_type: 业务类型
    """
    try:
        user_id = request.args.get('user_id')
        business_type = request.args.get('business_type', 'ai')
        
        if not user_id:
            return jsonify({'error': '用户ID不能为空'}), 400
        
        # 获取用户项目
        user_projects = MOCK_PROJECTS.get(user_id, [])
        
        # 根据业务类型过滤默认项目
        if business_type == 'ai':
            default_projects = [
                {
                    'id': 1,
                    'name': 'CNC机床主轴故障预测',
                    'status': 'running',
                    'type': 'local',
                    'trainingMode': 'normal',
                    'nodesOnline': 1,
                    'nodesTotal': 1,
                    'accuracy': 89.5,
                    'description': '基于深度学习的CNC机床主轴故障预测模型训练',
                    'created_at': '2024-01-15 10:00:00'
                }
            ]
        else:  # blockchain
            default_projects = [
                {
                    'id': 1,
                    'name': '信用风险评估模型',
                    'status': 'running',
                    'type': 'local',
                    'trainingMode': 'mpc',
                    'nodesOnline': 1,
                    'nodesTotal': 1,
                    'accuracy': 92.3,
                    'description': '基于区块链的信用风险评估联邦学习模型',
                    'created_at': '2024-01-15 10:00:00'
                }
            ]
        
        all_projects = default_projects + user_projects
        
        return jsonify({
            'success': True,
            'projects': all_projects
        }), 200
        
    except Exception as e:
        logging.error(f'获取项目列表错误: {str(e)}')
        return jsonify({'error': '获取项目列表失败'}), 500

@client_bp.route('/projects', methods=['POST'])
def create_project():
    """
    创建新项目
    
    请求参数:
    - name: 项目名称
    - description: 项目描述
    - type: 项目类型 (local/federated)
    """
    try:
        data = request.get_json()
        user_id = request.headers.get('X-User-Id')  # 从请求头获取用户ID
        
        if not user_id:
            return jsonify({'error': '用户身份验证失败'}), 401
        
        name = data.get('name')
        description = data.get('description', '')
        project_type = data.get('type', 'local')
        
        if not name:
            return jsonify({'error': '项目名称不能为空'}), 400
        
        training_mode = data.get('trainingMode', 'normal')
        
        # 创建项目
        new_project = {
            'id': len(MOCK_PROJECTS.get(user_id, [])) + 100,  # 避免与默认项目ID冲突
            'name': name,
            'description': description,
            'status': 'paused',
            'type': project_type,
            'trainingMode': training_mode,
            'nodesOnline': 0,
            'nodesTotal': 1 if project_type == 'local' else 0,
            'accuracy': 0.0,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 保存项目
        if user_id not in MOCK_PROJECTS:
            MOCK_PROJECTS[user_id] = []
        MOCK_PROJECTS[user_id].append(new_project)
        
        logging.info(f'项目创建成功: {name} (用户: {user_id})')
        
        return jsonify({
            'success': True,
            'project': new_project
        }), 201
        
    except Exception as e:
        logging.error(f'创建项目错误: {str(e)}')
        return jsonify({'error': '创建项目失败'}), 500

@client_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project_detail():
    """
    获取项目详情
    """
    try:
        user_id = request.headers.get('X-User-Id')
        
        if not user_id:
            return jsonify({'error': '用户身份验证失败'}), 401
        
        # 查找项目
        project = None
        user_projects = MOCK_PROJECTS.get(user_id, [])
        
        for p in user_projects:
            if p['id'] == project_id:
                project = p
                break
        
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        # 添加训练详情
        project_detail = {
            **project,
            'currentRound': 45 if project['status'] == 'running' else 0,
            'totalRounds': 100,
            'loss': 0.089 if project['status'] == 'running' else 0.0,
            'history': {
                'labels': list(range(1, 46)) if project['status'] == 'running' else [1, 2, 3],
                'accuracy': [0.6 + i * 0.01 for i in range(45)] if project['status'] == 'running' else [0.6, 0.65, 0.7]
            },
            'nodes': [
                {
                    'id': 1,
                    'name': user_id,
                    'status': '在线/训练中' if project['status'] == 'running' else '在线/等待',
                    'heartbeat': '3秒前',
                    'dataSize': '2.1 GB'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'project': project_detail
        }), 200
        
    except Exception as e:
        logging.error(f'获取项目详情错误: {str(e)}')
        return jsonify({'error': '获取项目详情失败'}), 500

@client_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project():
    """
    更新项目信息
    """
    try:
        user_id = request.headers.get('X-User-Id')
        data = request.get_json()
        
        if not user_id:
            return jsonify({'error': '用户身份验证失败'}), 401
        
        # 查找并更新项目
        user_projects = MOCK_PROJECTS.get(user_id, [])
        project_updated = False
        
        for i, project in enumerate(user_projects):
            if project['id'] == project_id:
                # 更新项目信息
                if 'name' in data:
                    project['name'] = data['name']
                if 'description' in data:
                    project['description'] = data['description']
                if 'status' in data:
                    project['status'] = data['status']
                    
                project['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                user_projects[i] = project
                project_updated = True
                break
        
        if not project_updated:
            return jsonify({'error': '项目不存在'}), 404
        
        return jsonify({
            'success': True,
            'message': '项目更新成功'
        }), 200
        
    except Exception as e:
        logging.error(f'更新项目错误: {str(e)}')
        return jsonify({'error': '更新项目失败'}), 500

@client_bp.route('/training-requests', methods=['POST'])
def submit_training_request():
    """
    提交联合训练申请
    
    请求参数:
    - projectName: 项目名称
    - dataDescription: 数据描述
    - trainingPlan: 训练计划
    - expectedPartners: 期望参与方数量
    """
    try:
        data = request.get_json()
        user_id = request.headers.get('X-User-Id')
        
        if not user_id:
            return jsonify({'error': '用户身份验证失败'}), 401
        
        project_name = data.get('projectName')
        data_description = data.get('dataDescription')
        training_plan = data.get('trainingPlan')
        expected_partners = data.get('expectedPartners', 3)
        
        if not all([project_name, data_description, training_plan]):
            return jsonify({'error': '请填写完整的申请信息'}), 400
        
        # 创建训练申请
        training_request = {
            'id': len(MOCK_TRAINING_REQUESTS) + 1,
            'clientName': user_id,
            'projectName': project_name,
            'dataDescription': data_description,
            'trainingPlan': training_plan,
            'expectedPartners': expected_partners,
            'currentPartners': 1,
            'status': 'pending',
            'requestTime': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'created_at': datetime.now().isoformat()
        }
        
        MOCK_TRAINING_REQUESTS.append(training_request)
        
        # 同时创建一个等待审批的项目
        waiting_project = {
            'id': len(MOCK_PROJECTS.get(user_id, [])) + 200,
            'name': project_name,
            'description': f'数据: {data_description}。计划: {training_plan}',
            'status': 'waiting_approval',
            'type': 'federated',
            'nodesOnline': 0,
            'nodesTotal': expected_partners,
            'accuracy': 0.0,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if user_id not in MOCK_PROJECTS:
            MOCK_PROJECTS[user_id] = []
        MOCK_PROJECTS[user_id].append(waiting_project)
        
        logging.info(f'联合训练申请提交成功: {project_name} (用户: {user_id})')
        
        return jsonify({
            'success': True,
            'request': training_request,
            'project': waiting_project
        }), 201
        
    except Exception as e:
        logging.error(f'提交训练申请错误: {str(e)}')
        return jsonify({'error': '提交训练申请失败'}), 500

@client_bp.route('/training-requests', methods=['GET'])
def get_training_requests():
    """
    获取客户端的训练申请列表
    """
    try:
        user_id = request.headers.get('X-User-Id')
        
        if not user_id:
            return jsonify({'error': '用户身份验证失败'}), 401
        
        # 过滤出该用户的申请
        user_requests = [req for req in MOCK_TRAINING_REQUESTS if req['clientName'] == user_id]
        
        return jsonify({
            'success': True,
            'requests': user_requests
        }), 200
        
    except Exception as e:
        logging.error(f'获取训练申请错误: {str(e)}')
        return jsonify({'error': '获取训练申请失败'}), 500

@client_bp.route('/training-data/<int:project_id>', methods=['GET'])
def get_training_data():
    """
    获取训练数据
    
    根据训练模式返回不同的数据：
    - 普通模式：返回完整的训练数据
    - MPC模式：返回加密或模糊化的数据
    """
    try:
        training_mode = request.args.get('mode', 'normal')  # normal or mpc
        user_id = request.headers.get('X-User-Id')
        
        if not user_id:
            return jsonify({'error': '用户身份验证失败'}), 401
        
        # 模拟训练数据
        if training_mode == 'mpc':
            # MPC模式下的模糊化数据
            training_data = {
                'accuracy': '***',  # 加密准确率
                'loss': '***',      # 加密损失值
                'rounds': 45,       # 轮次可见
                'encrypted_weights': 'encrypted_data_hash',
                'privacy_preserved': True
            }
        else:
            # 普通模式下的完整数据
            training_data = {
                'accuracy': 89.5,
                'loss': 0.089,
                'rounds': 45,
                'weights': [0.1, 0.2, 0.3],  # 示例权重
                'privacy_preserved': False
            }
        
        return jsonify({
            'success': True,
            'mode': training_mode,
            'data': training_data
        }), 200
        
    except Exception as e:
        logging.error(f'获取训练数据错误: {str(e)}')
        return jsonify({'error': '获取训练数据失败'}), 500