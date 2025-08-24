"""
AI模块模型管理相关路由
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import uuid

from shared.middleware.auth import auth_required, business_type_required
from shared.utils.helpers import success_response, error_response, safe_int
from shared.utils.validators import (
    validate_request_data, validate_model_type
)
from shared.services.user_service import UserService
from models.model import Model
from models.training_session import TrainingSession
from models.base import db

models_bp = Blueprint('models', __name__)


@models_bp.route('/create', methods=['POST'])
@auth_required
@business_type_required(['ai'])
def create_model():
    """创建新模型"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # 验证请求数据
        required_fields = ['name', 'model_type', 'architecture']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        # 验证模型类型
        if not validate_model_type(data['model_type']):
            return error_response('无效的模型类型')
        
        # 创建模型
        model = Model(
            user_id=user_id,
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            model_type=data['model_type'],
            architecture=data['architecture'],
            hyperparameters=data.get('hyperparameters', {}),
            status='created',
            accuracy=0.0,
            loss=0.0
        )
        
        db.session.add(model)
        db.session.commit()
        
        return success_response({
            'model_id': model.id,
            'name': model.name,
            'model_type': model.model_type,
            'architecture': model.architecture,
            'status': model.status,
            'created_at': model.created_at.isoformat()
        }, '模型创建成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建模型失败: {str(e)}', 500)


@models_bp.route('/list', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def get_models():
    """获取用户模型列表"""
    try:
        user_id = session.get('user_id')
        page = safe_int(request.args.get('page', 1), 1)
        per_page = safe_int(request.args.get('per_page', 10), 10)
        status = request.args.get('status')
        model_type = request.args.get('model_type')
        
        # 构建查询
        query = Model.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if model_type and validate_model_type(model_type):
            query = query.filter_by(model_type=model_type)
        
        # 分页查询
        models = query.order_by(Model.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        models_data = []
        for model in models.items:
            # 获取模型相关的训练会话数量
            sessions_count = TrainingSession.query.filter_by(model_id=model.id).count()
            
            models_data.append({
                'id': model.id,
                'name': model.name,
                'description': model.description,
                'model_type': model.model_type,
                'architecture': model.architecture,
                'status': model.status,
                'accuracy': float(model.accuracy) if model.accuracy else 0.0,
                'loss': float(model.loss) if model.loss else 0.0,
                'sessions_count': sessions_count,
                'created_at': model.created_at.isoformat(),
                'updated_at': model.updated_at.isoformat() if model.updated_at else None
            })
        
        return success_response({
            'models': models_data,
            'total': models.total,
            'pages': models.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return error_response(f'获取模型列表失败: {str(e)}', 500)


@models_bp.route('/<int:model_id>', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def get_model_detail(model_id):
    """获取模型详情"""
    try:
        user_id = session.get('user_id')
        
        model = Model.query.filter_by(id=model_id, user_id=user_id).first()
        if not model:
            return error_response('模型不存在', 404)
        
        # 获取模型的训练会话
        sessions = TrainingSession.query.filter_by(model_id=model.id).order_by(
            TrainingSession.created_at.desc()
        ).limit(5).all()
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'session_id': session.session_id,
                'status': session.status,
                'current_round': session.current_round,
                'total_rounds': session.total_rounds,
                'accuracy': float(session.accuracy) if session.accuracy else 0.0,
                'loss': float(session.loss) if session.loss else 0.0,
                'created_at': session.created_at.isoformat(),
                'completed_at': session.completed_at.isoformat() if session.completed_at else None
            })
        
        return success_response({
            'id': model.id,
            'name': model.name,
            'description': model.description,
            'model_type': model.model_type,
            'architecture': model.architecture,
            'hyperparameters': model.hyperparameters,
            'status': model.status,
            'accuracy': float(model.accuracy) if model.accuracy else 0.0,
            'loss': float(model.loss) if model.loss else 0.0,
            'created_at': model.created_at.isoformat(),
            'updated_at': model.updated_at.isoformat() if model.updated_at else None,
            'recent_sessions': sessions_data
        })
        
    except Exception as e:
        return error_response(f'获取模型详情失败: {str(e)}', 500)


@models_bp.route('/<int:model_id>', methods=['PUT'])
@auth_required
@business_type_required(['ai'])
def update_model(model_id):
    """更新模型信息"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        model = Model.query.filter_by(id=model_id, user_id=user_id).first()
        if not model:
            return error_response('模型不存在', 404)
        
        # 更新模型信息
        if 'name' in data:
            model.name = data['name'].strip()
        
        if 'description' in data:
            model.description = data['description'].strip()
        
        if 'hyperparameters' in data:
            model.hyperparameters = data['hyperparameters']
        
        if 'status' in data and data['status'] in ['created', 'training', 'trained', 'deployed']:
            model.status = data['status']
        
        model.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response({
            'id': model.id,
            'name': model.name,
            'description': model.description,
            'status': model.status,
            'updated_at': model.updated_at.isoformat()
        }, '模型更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新模型失败: {str(e)}', 500)


@models_bp.route('/<int:model_id>', methods=['DELETE'])
@auth_required
@business_type_required(['ai'])
def delete_model(model_id):
    """删除模型"""
    try:
        user_id = session.get('user_id')
        
        model = Model.query.filter_by(id=model_id, user_id=user_id).first()
        if not model:
            return error_response('模型不存在', 404)
        
        # 检查是否有正在进行的训练会话
        active_sessions = TrainingSession.query.filter_by(
            model_id=model.id,
            status='running'
        ).count()
        
        if active_sessions > 0:
            return error_response('模型有正在进行的训练会话，无法删除')
        
        # 删除相关的训练会话
        TrainingSession.query.filter_by(model_id=model.id).delete()
        
        # 删除模型
        db.session.delete(model)
        db.session.commit()
        
        return success_response(None, '模型删除成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除模型失败: {str(e)}', 500)


@models_bp.route('/<int:model_id>/train', methods=['POST'])
@auth_required
@business_type_required(['ai'])
def train_model():
    """开始模型训练"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # 验证请求数据
        required_fields = ['model_id', 'dataset_id', 'training_config']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        model = Model.query.filter_by(id=data['model_id'], user_id=user_id).first()
        if not model:
            return error_response('模型不存在', 404)
        
        if model.status == 'training':
            return error_response('模型正在训练中')
        
        # 创建训练会话
        session_id = f"training_{uuid.uuid4().hex[:12]}"
        training_session = TrainingSession(
            model_id=model.id,
            session_id=session_id,
            training_mode='normal',
            model_type=model.model_type,
            total_rounds=data['training_config'].get('epochs', 10),
            current_round=0,
            status='running',
            accuracy=0.0,
            loss=0.0,
            participants_count=1
        )
        
        db.session.add(training_session)
        
        # 更新模型状态
        model.status = 'training'
        model.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return success_response({
            'session_id': session_id,
            'training_id': training_session.id,
            'status': 'running',
            'model_name': model.name
        }, '模型训练已开始')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'开始模型训练失败: {str(e)}', 500)


@models_bp.route('/<int:model_id>/evaluate', methods=['POST'])
@auth_required
@business_type_required(['ai'])
def evaluate_model(model_id):
    """评估模型性能"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        model = Model.query.filter_by(id=model_id, user_id=user_id).first()
        if not model:
            return error_response('模型不存在', 404)
        
        if model.status != 'trained':
            return error_response('模型未训练完成，无法评估')
        
        # 模拟评估过程
        evaluation_results = {
            'accuracy': 0.92,
            'precision': 0.89,
            'recall': 0.94,
            'f1_score': 0.915,
            'loss': 0.08,
            'evaluated_at': datetime.utcnow().isoformat(),
            'test_samples': data.get('test_samples', 1000)
        }
        
        return success_response({
            'model_id': model_id,
            'evaluation_results': evaluation_results
        }, '模型评估完成')
        
    except Exception as e:
        return error_response(f'模型评估失败: {str(e)}', 500)


@models_bp.route('/<int:model_id>/deploy', methods=['POST'])
@auth_required
@business_type_required(['ai'])
def deploy_model(model_id):
    """部署模型"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        model = Model.query.filter_by(id=model_id, user_id=user_id).first()
        if not model:
            return error_response('模型不存在', 404)
        
        if model.status not in ['trained']:
            return error_response('模型未训练完成，无法部署')
        
        # 更新模型状态
        model.status = 'deployed'
        model.updated_at = datetime.utcnow()
        db.session.commit()
        
        deployment_info = {
            'model_id': model_id,
            'deployment_url': f"/api/ai/models/{model_id}/predict",
            'status': 'deployed',
            'deployed_at': datetime.utcnow().isoformat(),
            'environment': data.get('environment', 'production')
        }
        
        return success_response(deployment_info, '模型部署成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'模型部署失败: {str(e)}', 500)


@models_bp.route('/templates', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def get_model_templates():
    """获取模型模板列表"""
    try:
        templates = [
            {
                'id': 'cnn_image_classifier',
                'name': 'CNN图像分类器',
                'description': '基于卷积神经网络的图像分类模型',
                'model_type': 'cnn',
                'architecture': 'CNN',
                'task_type': 'image_classification',
                'default_config': {
                    'layers': [
                        {'type': 'Conv2D', 'filters': 32, 'kernel_size': 3, 'activation': 'relu'},
                        {'type': 'MaxPooling2D', 'pool_size': 2},
                        {'type': 'Conv2D', 'filters': 64, 'kernel_size': 3, 'activation': 'relu'},
                        {'type': 'MaxPooling2D', 'pool_size': 2},
                        {'type': 'Flatten'},
                        {'type': 'Dense', 'units': 128, 'activation': 'relu'},
                        {'type': 'Dense', 'units': 10, 'activation': 'softmax'}
                    ]
                }
            },
            {
                'id': 'lstm_text_classifier',
                'name': 'LSTM文本分类器',
                'description': '基于长短期记忆网络的文本分类模型',
                'model_type': 'lstm',
                'architecture': 'LSTM',
                'task_type': 'text_classification',
                'default_config': {
                    'layers': [
                        {'type': 'Embedding', 'input_dim': 10000, 'output_dim': 128},
                        {'type': 'LSTM', 'units': 64, 'dropout': 0.2},
                        {'type': 'Dense', 'units': 64, 'activation': 'relu'},
                        {'type': 'Dense', 'units': 5, 'activation': 'softmax'}
                    ]
                }
            },
            {
                'id': 'mlp_regressor',
                'name': 'MLP回归器',
                'description': '基于多层感知器的回归预测模型',
                'model_type': 'mlp',
                'architecture': 'MLP',
                'task_type': 'regression',
                'default_config': {
                    'layers': [
                        {'type': 'Dense', 'units': 256, 'activation': 'relu'},
                        {'type': 'Dropout', 'rate': 0.3},
                        {'type': 'Dense', 'units': 128, 'activation': 'relu'},
                        {'type': 'Dropout', 'rate': 0.3},
                        {'type': 'Dense', 'units': 1, 'activation': 'linear'}
                    ]
                }
            }
        ]
        
        # 应用过滤器
        model_type = request.args.get('model_type')
        task_type = request.args.get('task_type')
        
        if model_type:
            templates = [t for t in templates if t['model_type'] == model_type]
        
        if task_type:
            templates = [t for t in templates if t['task_type'] == task_type]
        
        return success_response({
            'templates': templates,
            'total': len(templates)
        })
        
    except Exception as e:
        return error_response(f'获取模型模板失败: {str(e)}', 500)