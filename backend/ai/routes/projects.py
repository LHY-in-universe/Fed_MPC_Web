"""
AI模块项目管理相关路由
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import uuid

from shared.middleware.auth import auth_required, business_type_required
from shared.utils.helpers import success_response, error_response, safe_int
from shared.utils.validators import (
    validate_request_data, validate_project_type, validate_training_mode
)
from shared.services.user_service import UserService
from models.project import Project
from models.training_session import TrainingSession
from models.base import db

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/create', methods=['POST'])
@auth_required
@business_type_required(['ai'])
def create_project():
    """创建新项目"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # 验证请求数据
        required_fields = ['name', 'description', 'project_type', 'training_mode']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        # 验证项目类型和训练模式
        if not validate_project_type(data['project_type']):
            return error_response('无效的项目类型')
        
        if not validate_training_mode(data['training_mode']):
            return error_response('无效的训练模式')
        
        # 创建项目
        project = Project(
            user_id=user_id,
            name=data['name'].strip(),
            description=data['description'].strip(),
            project_type=data['project_type'],
            training_mode=data['training_mode'],
            status='active',
            model_config=data.get('model_config', {}),
            privacy_level=data.get('privacy_level', 'standard')
        )
        
        db.session.add(project)
        db.session.commit()
        
        return success_response({
            'project_id': project.id,
            'name': project.name,
            'project_type': project.project_type,
            'training_mode': project.training_mode,
            'status': project.status,
            'created_at': project.created_at.isoformat()
        }, '项目创建成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建项目失败: {str(e)}', 500)


@projects_bp.route('/list', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def get_projects():
    """获取用户项目列表"""
    try:
        user_id = session.get('user_id')
        page = safe_int(request.args.get('page', 1), 1)
        per_page = safe_int(request.args.get('per_page', 10), 10)
        status = request.args.get('status')
        project_type = request.args.get('project_type')
        
        # 构建查询
        query = Project.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if project_type and validate_project_type(project_type):
            query = query.filter_by(project_type=project_type)
        
        # 分页查询
        projects = query.order_by(Project.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        projects_data = []
        for project in projects.items:
            # 获取项目相关的训练会话数量
            sessions_count = TrainingSession.query.filter_by(project_id=project.id).count()
            
            projects_data.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'project_type': project.project_type,
                'training_mode': project.training_mode,
                'status': project.status,
                'privacy_level': project.privacy_level,
                'sessions_count': sessions_count,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat() if project.updated_at else None
            })
        
        return success_response({
            'projects': projects_data,
            'total': projects.total,
            'pages': projects.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return error_response(f'获取项目列表失败: {str(e)}', 500)


@projects_bp.route('/<int:project_id>', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def get_project_detail(project_id):
    """获取项目详情"""
    try:
        user_id = session.get('user_id')
        
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        if not project:
            return error_response('项目不存在', 404)
        
        # 获取项目的训练会话
        sessions = TrainingSession.query.filter_by(project_id=project.id).order_by(
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
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'project_type': project.project_type,
            'training_mode': project.training_mode,
            'status': project.status,
            'privacy_level': project.privacy_level,
            'model_config': project.model_config,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat() if project.updated_at else None,
            'recent_sessions': sessions_data
        })
        
    except Exception as e:
        return error_response(f'获取项目详情失败: {str(e)}', 500)


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@auth_required
@business_type_required(['ai'])
def update_project(project_id):
    """更新项目信息"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        if not project:
            return error_response('项目不存在', 404)
        
        # 更新项目信息
        if 'name' in data:
            project.name = data['name'].strip()
        
        if 'description' in data:
            project.description = data['description'].strip()
        
        if 'status' in data and data['status'] in ['active', 'paused', 'completed']:
            project.status = data['status']
        
        if 'model_config' in data:
            project.model_config = data['model_config']
        
        if 'privacy_level' in data and data['privacy_level'] in ['standard', 'mpc']:
            project.privacy_level = data['privacy_level']
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'status': project.status,
            'updated_at': project.updated_at.isoformat()
        }, '项目更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新项目失败: {str(e)}', 500)


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@auth_required
@business_type_required(['ai'])
def delete_project(project_id):
    """删除项目"""
    try:
        user_id = session.get('user_id')
        
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        if not project:
            return error_response('项目不存在', 404)
        
        # 检查是否有正在进行的训练会话
        active_sessions = TrainingSession.query.filter_by(
            project_id=project.id,
            status='running'
        ).count()
        
        if active_sessions > 0:
            return error_response('项目有正在进行的训练会话，无法删除')
        
        # 删除相关的训练会话
        TrainingSession.query.filter_by(project_id=project.id).delete()
        
        # 删除项目
        db.session.delete(project)
        db.session.commit()
        
        return success_response(None, '项目删除成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除项目失败: {str(e)}', 500)


@projects_bp.route('/federated/join-request', methods=['POST'])
@auth_required
@business_type_required(['ai'])
def request_join_federated():
    """申请加入联邦训练"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # 验证请求数据
        required_fields = ['project_id', 'local_data_size', 'compute_capability']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        project = Project.query.filter_by(id=data['project_id'], user_id=user_id).first()
        if not project:
            return error_response('项目不存在', 404)
        
        if project.project_type != 'federated':
            return error_response('只有联邦项目可以申请加入联邦训练')
        
        # 创建加入申请记录
        join_request = {
            'project_id': project.id,
            'user_id': user_id,
            'local_data_size': data['local_data_size'],
            'compute_capability': data['compute_capability'],
            'training_mode': project.training_mode,
            'status': 'pending',
            'requested_at': datetime.utcnow().isoformat(),
            'message': data.get('message', '')
        }
        
        # 这里应该存储到专门的申请表中，暂时返回成功响应
        return success_response({
            'request_id': f"req_{uuid.uuid4().hex[:12]}",
            'status': 'pending',
            'project_name': project.name,
            'training_mode': project.training_mode
        }, '联邦训练申请已提交')
        
    except Exception as e:
        return error_response(f'申请加入联邦训练失败: {str(e)}', 500)