"""
训练相关路由
处理联邦学习训练过程、数据同步、模型聚合等功能
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
import random
import json

training_bp = Blueprint('training', __name__)

# 模拟训练数据存储
MOCK_TRAINING_SESSIONS = {}
MOCK_TRAINING_LOGS = {}

@training_bp.route('/sessions', methods=['POST'])
def create_training_session():
    """
    创建训练会话
    
    请求参数:
    - projectId: 项目ID
    - participants: 参与方列表
    - trainingMode: 训练模式 (normal/mpc)
    - modelType: 模型类型
    - totalRounds: 总轮次
    """
    try:
        data = request.get_json()
        
        project_id = data.get('projectId')
        participants = data.get('participants', [])
        training_mode = data.get('trainingMode', 'normal')
        model_type = data.get('modelType', 'CNN')
        total_rounds = data.get('totalRounds', 100)
        
        if not project_id or not participants:
            return jsonify({'error': '项目ID和参与方不能为空'}), 400
        
        # 创建训练会话
        session_id = f"session_{project_id}_{int(datetime.now().timestamp())}"
        
        training_session = {
            'sessionId': session_id,
            'projectId': project_id,
            'participants': participants,
            'trainingMode': training_mode,
            'modelType': model_type,
            'totalRounds': total_rounds,
            'currentRound': 0,
            'status': 'created',
            'accuracy': 0.0,
            'loss': 1.0,
            'startTime': None,
            'endTime': None,
            'createdAt': datetime.now().isoformat(),
            'logs': []
        }
        
        MOCK_TRAINING_SESSIONS[session_id] = training_session
        MOCK_TRAINING_LOGS[session_id] = []
        
        logging.info(f'训练会话创建成功: {session_id}')
        
        return jsonify({
            'success': True,
            'session': training_session
        }), 201
        
    except Exception as e:
        logging.error(f'创建训练会话错误: {str(e)}')
        return jsonify({'error': '创建训练会话失败'}), 500

@training_bp.route('/sessions/<session_id>/start', methods=['POST'])
def start_training():
    """
    开始训练
    """
    try:
        session = MOCK_TRAINING_SESSIONS.get(session_id)
        
        if not session:
            return jsonify({'error': '训练会话不存在'}), 404
        
        if session['status'] != 'created':
            return jsonify({'error': '训练会话状态不正确'}), 400
        
        # 更新会话状态
        session['status'] = 'running'
        session['startTime'] = datetime.now().isoformat()
        
        # 添加开始训练日志
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'round': 0,
            'event': 'training_started',
            'message': '联邦学习训练开始',
            'participants': session['participants']
        }
        
        MOCK_TRAINING_LOGS[session_id].append(log_entry)
        session['logs'].append(log_entry)
        
        logging.info(f'训练开始: {session_id}')
        
        return jsonify({
            'success': True,
            'message': '训练已开始'
        }), 200
        
    except Exception as e:
        logging.error(f'开始训练错误: {str(e)}')
        return jsonify({'error': '开始训练失败'}), 500

@training_bp.route('/sessions/<session_id>/round', methods=['POST'])
def submit_round_data():
    """
    提交训练轮次数据
    
    请求参数:
    - clientId: 客户端ID
    - round: 轮次
    - localAccuracy: 本地准确率
    - localLoss: 本地损失
    - modelWeights: 模型权重 (普通模式)
    - encryptedWeights: 加密权重 (MPC模式)
    """
    try:
        data = request.get_json()
        session = MOCK_TRAINING_SESSIONS.get(session_id)
        
        if not session:
            return jsonify({'error': '训练会话不存在'}), 404
        
        client_id = data.get('clientId')
        round_num = data.get('round')
        local_accuracy = data.get('localAccuracy')
        local_loss = data.get('localLoss')
        
        if not all([client_id, round_num is not None, local_accuracy is not None, local_loss is not None]):
            return jsonify({'error': '缺少必要的训练数据'}), 400
        
        # 模拟全局模型聚合
        if session['trainingMode'] == 'mpc':
            # MPC模式：加密聚合
            aggregated_accuracy = session['accuracy'] + random.uniform(0.1, 0.5)
            aggregated_loss = max(session['loss'] * random.uniform(0.95, 0.98), 0.01)
            weights_info = 'encrypted_aggregated_weights'
        else:
            # 普通模式：明文聚合
            aggregated_accuracy = session['accuracy'] + random.uniform(0.1, 0.5)
            aggregated_loss = max(session['loss'] * random.uniform(0.95, 0.98), 0.01)
            weights_info = {'layer1': [0.1, 0.2], 'layer2': [0.3, 0.4]}  # 示例权重
        
        # 更新会话数据
        session['currentRound'] = round_num
        session['accuracy'] = min(aggregated_accuracy, 99.9)
        session['loss'] = aggregated_loss
        
        # 添加训练日志
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'round': round_num,
            'event': 'round_completed',
            'clientId': client_id,
            'localAccuracy': local_accuracy,
            'localLoss': local_loss,
            'globalAccuracy': session['accuracy'],
            'globalLoss': session['loss'],
            'message': f'第{round_num}轮训练完成'
        }
        
        MOCK_TRAINING_LOGS[session_id].append(log_entry)
        session['logs'].append(log_entry)
        
        # 检查是否完成训练
        if round_num >= session['totalRounds']:
            session['status'] = 'completed'
            session['endTime'] = datetime.now().isoformat()
            
            completion_log = {
                'timestamp': datetime.now().isoformat(),
                'round': round_num,
                'event': 'training_completed',
                'message': '联邦学习训练完成',
                'finalAccuracy': session['accuracy'],
                'finalLoss': session['loss']
            }
            
            MOCK_TRAINING_LOGS[session_id].append(completion_log)
            session['logs'].append(completion_log)
        
        response_data = {
            'success': True,
            'round': round_num,
            'globalAccuracy': session['accuracy'],
            'globalLoss': session['loss'] if session['trainingMode'] == 'normal' else '***',
            'status': session['status']
        }
        
        if session['trainingMode'] == 'normal':
            response_data['aggregatedWeights'] = weights_info
        else:
            response_data['encryptedWeights'] = weights_info
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f'提交训练数据错误: {str(e)}')
        return jsonify({'error': '提交训练数据失败'}), 500

@training_bp.route('/sessions/<session_id>', methods=['GET'])
def get_training_session():
    """
    获取训练会话详情
    """
    try:
        session = MOCK_TRAINING_SESSIONS.get(session_id)
        
        if not session:
            return jsonify({'error': '训练会话不存在'}), 404
        
        return jsonify({
            'success': True,
            'session': session
        }), 200
        
    except Exception as e:
        logging.error(f'获取训练会话错误: {str(e)}')
        return jsonify({'error': '获取训练会话失败'}), 500

@training_bp.route('/sessions/<session_id>/logs', methods=['GET'])
def get_training_logs():
    """
    获取训练日志
    """
    try:
        logs = MOCK_TRAINING_LOGS.get(session_id, [])
        
        # 分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_logs = logs[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'logs': paginated_logs,
            'total': len(logs),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(logs) + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        logging.error(f'获取训练日志错误: {str(e)}')
        return jsonify({'error': '获取训练日志失败'}), 500

@training_bp.route('/sessions/<session_id>/stop', methods=['POST'])
def stop_training():
    """
    停止训练
    """
    try:
        session = MOCK_TRAINING_SESSIONS.get(session_id)
        
        if not session:
            return jsonify({'error': '训练会话不存在'}), 404
        
        if session['status'] != 'running':
            return jsonify({'error': '训练未在运行中'}), 400
        
        # 更新会话状态
        session['status'] = 'stopped'
        session['endTime'] = datetime.now().isoformat()
        
        # 添加停止训练日志
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'round': session['currentRound'],
            'event': 'training_stopped',
            'message': '训练已手动停止'
        }
        
        MOCK_TRAINING_LOGS[session_id].append(log_entry)
        session['logs'].append(log_entry)
        
        logging.info(f'训练停止: {session_id}')
        
        return jsonify({
            'success': True,
            'message': '训练已停止'
        }), 200
        
    except Exception as e:
        logging.error(f'停止训练错误: {str(e)}')
        return jsonify({'error': '停止训练失败'}), 500

@training_bp.route('/sessions/<session_id>/heartbeat', methods=['POST'])
def client_heartbeat():
    """
    客户端心跳接口
    """
    try:
        data = request.get_json()
        client_id = data.get('clientId')
        status = data.get('status', 'online')
        
        if not client_id:
            return jsonify({'error': '客户端ID不能为空'}), 400
        
        session = MOCK_TRAINING_SESSIONS.get(session_id)
        
        if not session:
            return jsonify({'error': '训练会话不存在'}), 404
        
        # 更新客户端状态
        heartbeat_log = {
            'timestamp': datetime.now().isoformat(),
            'round': session['currentRound'],
            'event': 'client_heartbeat',
            'clientId': client_id,
            'status': status,
            'message': f'客户端{client_id}心跳更新'
        }
        
        MOCK_TRAINING_LOGS[session_id].append(heartbeat_log)
        
        return jsonify({
            'success': True,
            'message': '心跳更新成功',
            'serverTime': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f'客户端心跳错误: {str(e)}')
        return jsonify({'error': '心跳更新失败'}), 500

@training_bp.route('/statistics', methods=['GET'])
def get_training_statistics():
    """
    获取训练统计信息
    """
    try:
        business_type = request.args.get('business_type', 'ai')
        
        # 计算统计数据
        total_sessions = len(MOCK_TRAINING_SESSIONS)
        active_sessions = len([s for s in MOCK_TRAINING_SESSIONS.values() if s['status'] == 'running'])
        completed_sessions = len([s for s in MOCK_TRAINING_SESSIONS.values() if s['status'] == 'completed'])
        
        avg_accuracy = 0
        if completed_sessions > 0:
            total_accuracy = sum([s['accuracy'] for s in MOCK_TRAINING_SESSIONS.values() if s['status'] == 'completed'])
            avg_accuracy = total_accuracy / completed_sessions
        
        statistics = {
            'totalSessions': total_sessions,
            'activeSessions': active_sessions,
            'completedSessions': completed_sessions,
            'averageAccuracy': round(avg_accuracy, 2),
            'businessType': business_type,
            'generatedAt': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        }), 200
        
    except Exception as e:
        logging.error(f'获取训练统计错误: {str(e)}')
        return jsonify({'error': '获取训练统计失败'}), 500