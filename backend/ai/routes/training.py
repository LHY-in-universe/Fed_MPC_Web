"""
AI模块训练相关路由
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import uuid
import json

from shared.middleware.auth import auth_required, business_type_required
from shared.utils.helpers import success_response, error_response, safe_int, safe_float
from shared.utils.validators import (
    validate_request_data, validate_training_config, validate_model_type,
    validate_learning_rate, validate_epochs, validate_batch_size
)
from shared.services.user_service import UserService
from models.training_session import TrainingSession
from models.training_round import TrainingRound
from models.project import Project
from models.base import db

training_bp = Blueprint('training', __name__)


@training_bp.route('/local/start', methods=['POST'])
@auth_required
@business_type_required(['ai'])
def start_local_training():
    """开始本地训练"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # 验证请求数据
        required_fields = ['model_type', 'learning_rate', 'epochs', 'batch_size', 'dataset_id']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        # 验证训练配置
        config_validation = validate_training_config(data)
        if not config_validation['valid']:
            return error_response(config_validation['message'])
        
        # 创建训练会话
        session_id = f"local_{uuid.uuid4().hex[:12]}"
        training_session = TrainingSession(
            project_id=None,  # 本地训练没有项目ID
            session_id=session_id,
            training_mode='normal',
            model_type=data['model_type'],
            total_rounds=data['epochs'],
            current_round=0,
            status='created',
            accuracy=0.0,
            loss=0.0,
            participants_count=1
        )
        
        db.session.add(training_session)
        db.session.commit()
        
        # 记录训练配置
        training_config = {
            'learning_rate': data['learning_rate'],
            'batch_size': data['batch_size'],
            'dataset_id': data['dataset_id'],
            'validation_split': data.get('validation_split', 0.2),
            'augmentation': data.get('augmentation', {}),
            'user_id': user_id
        }
        
        return success_response({
            'session_id': session_id,
            'training_id': training_session.id,
            'status': 'created',
            'config': training_config
        }, '本地训练会话创建成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建训练会话失败: {str(e)}', 500)


@training_bp.route('/local/status/<session_id>', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def get_local_training_status(session_id):
    """获取本地训练状态"""
    try:
        training_session = TrainingSession.query.filter_by(session_id=session_id).first()
        
        if not training_session:
            return error_response('训练会话不存在', 404)
        
        # 获取最新的训练轮次数据
        latest_round = TrainingRound.query.filter_by(
            session_id=training_session.id
        ).order_by(TrainingRound.round_number.desc()).first()
        
        response_data = {
            'session_id': session_id,
            'status': training_session.status,
            'current_round': training_session.current_round,
            'total_rounds': training_session.total_rounds,
            'accuracy': float(training_session.accuracy) if training_session.accuracy else 0.0,
            'loss': float(training_session.loss) if training_session.loss else 0.0,
            'started_at': training_session.started_at.isoformat() if training_session.started_at else None,
            'completed_at': training_session.completed_at.isoformat() if training_session.completed_at else None
        }
        
        if latest_round:
            response_data['latest_round'] = {
                'round_number': latest_round.round_number,
                'accuracy': float(latest_round.global_accuracy) if latest_round.global_accuracy else 0.0,
                'loss': float(latest_round.global_loss) if latest_round.global_loss else 0.0,
                'completed_at': latest_round.completed_at.isoformat() if latest_round.completed_at else None
            }
        
        return success_response(response_data)
        
    except Exception as e:
        return error_response(f'获取训练状态失败: {str(e)}', 500)


@training_bp.route('/history', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def get_training_history():
    """获取训练历史"""
    try:
        user_id = session.get('user_id')
        
        # 获取用户的训练会话
        sessions = TrainingSession.query.join(Project).filter(
            Project.user_id == user_id
        ).order_by(TrainingSession.created_at.desc()).limit(10).all()
        
        history_data = []
        for session in sessions:
            # 获取训练轮次历史
            rounds = TrainingRound.query.filter_by(
                session_id=session.id
            ).order_by(TrainingRound.round_number.asc()).all()
            
            rounds_data = []
            for round_obj in rounds:
                rounds_data.append({
                    'round_number': round_obj.round_number,
                    'accuracy': float(round_obj.global_accuracy) if round_obj.global_accuracy else 0.0,
                    'loss': float(round_obj.global_loss) if round_obj.global_loss else 0.0,
                    'completed_at': round_obj.completed_at.isoformat() if round_obj.completed_at else None
                })
            
            history_data.append({
                'session_id': session.session_id,
                'model_type': session.model_type,
                'training_mode': session.training_mode,
                'status': session.status,
                'final_accuracy': float(session.accuracy) if session.accuracy else 0.0,
                'final_loss': float(session.loss) if session.loss else 0.0,
                'total_rounds': session.total_rounds,
                'completed_rounds': session.current_round,
                'created_at': session.created_at.isoformat(),
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'rounds': rounds_data
            })
        
        return success_response({
            'history': history_data,
            'total': len(history_data)
        })
        
    except Exception as e:
        return error_response(f'获取训练历史失败: {str(e)}', 500)