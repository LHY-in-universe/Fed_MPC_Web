"""
EdgeAI项目管理路由
"""

from flask import Blueprint, request, jsonify
from models.base import db
from models.user import User
from edgeai.models import EdgeAIProject, EdgeNode, ControlNode
from datetime import datetime
from sqlalchemy import desc

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/', methods=['GET'])
def list_projects():
    """获取项目列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        query = EdgeAIProject.query
        
        # 搜索过滤
        if search:
            query = query.filter(EdgeAIProject.name.contains(search))
        
        # 状态过滤
        if status:
            query = query.filter(EdgeAIProject.status == status)
        
        # 分页
        projects = query.order_by(desc(EdgeAIProject.updated_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'projects': [project.to_dict() for project in projects.items],
                'total': projects.total,
                'pages': projects.pages,
                'current_page': page,
                'has_next': projects.has_next,
                'has_prev': projects.has_prev
            }
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取项目列表失败: {str(e)}'
        }), 500

@projects_bp.route('/', methods=['POST'])
def create_project():
    """创建新项目"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'owner_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}'
                }), 400
        
        # 检查所有者是否存在
        owner = User.query.get(data['owner_id'])
        if not owner:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        # 创建项目
        project = EdgeAIProject(
            name=data['name'],
            description=data.get('description', ''),
            owner_id=data['owner_id'],
            ai_model_type=data.get('ai_model_type', 'CNN'),
            training_strategy=data.get('training_strategy', 'federated'),
            max_nodes=data.get('max_nodes', 50),
            target_accuracy=data.get('target_accuracy', 90)
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'code': 201,
            'message': '项目创建成功',
            'data': project.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建项目失败: {str(e)}'
        }), 500

@projects_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """获取项目详情"""
    try:
        project = EdgeAIProject.query.get_or_404(project_id)
        
        # 获取项目统计信息
        project_data = project.to_dict()
        project_data['statistics'] = project.get_statistics()
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': project_data
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取项目详情失败: {str(e)}'
        }), 500

@projects_bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """更新项目"""
    try:
        project = EdgeAIProject.query.get_or_404(project_id)
        data = request.get_json()
        
        # 更新字段
        updatable_fields = ['name', 'description', 'ai_model_type', 'training_strategy', 
                          'max_nodes', 'target_accuracy', 'status']
        
        for field in updatable_fields:
            if field in data:
                setattr(project, field, data[field])
        
        # 如果状态变为training，设置开始时间
        if data.get('status') == 'training' and not project.started_at:
            project.started_at = datetime.utcnow()
        
        # 如果状态变为completed，设置完成时间
        if data.get('status') == 'completed' and not project.completed_at:
            project.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '项目更新成功',
            'data': project.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新项目失败: {str(e)}'
        }), 500

@projects_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    try:
        project = EdgeAIProject.query.get_or_404(project_id)
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '项目删除成功'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除项目失败: {str(e)}'
        }), 500

@projects_bp.route('/<int:project_id>/start', methods=['POST'])
def start_project(project_id):
    """启动项目训练"""
    try:
        project = EdgeAIProject.query.get_or_404(project_id)
        
        # 检查项目是否可以启动
        if project.status in ['training', 'completed']:
            return jsonify({
                'code': 400,
                'message': '项目已经在训练或已完成'
            }), 400
        
        # 检查是否有足够的节点
        if len(project.edge_nodes) == 0:
            return jsonify({
                'code': 400,
                'message': '项目没有边缘节点，无法启动训练'
            }), 400
        
        # 启动项目
        project.status = 'training'
        project.started_at = datetime.utcnow()
        
        # 将所有边缘节点状态设置为训练中
        for node in project.edge_nodes:
            if node.status == 'online':
                node.status = 'training'
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '项目训练启动成功',
            'data': project.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'启动项目失败: {str(e)}'
        }), 500

@projects_bp.route('/<int:project_id>/pause', methods=['POST'])
def pause_project(project_id):
    """暂停项目训练"""
    try:
        project = EdgeAIProject.query.get_or_404(project_id)
        
        if project.status != 'training':
            return jsonify({
                'code': 400,
                'message': '只能暂停正在训练的项目'
            }), 400
        
        # 暂停项目
        project.status = 'paused'
        
        # 暂停所有训练中的节点
        for node in project.edge_nodes:
            if node.status == 'training':
                node.status = 'idle'
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '项目训练暂停成功',
            'data': project.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'暂停项目失败: {str(e)}'
        }), 500

@projects_bp.route('/<int:project_id>/resume', methods=['POST'])
def resume_project(project_id):
    """恢复项目训练"""
    try:
        project = EdgeAIProject.query.get_or_404(project_id)
        
        if project.status != 'paused':
            return jsonify({
                'code': 400,
                'message': '只能恢复暂停的项目'
            }), 400
        
        # 恢复项目
        project.status = 'training'
        
        # 恢复空闲节点的训练
        for node in project.edge_nodes:
            if node.status == 'idle':
                node.status = 'training'
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '项目训练恢复成功',
            'data': project.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'恢复项目失败: {str(e)}'
        }), 500

@projects_bp.route('/<int:project_id>/statistics', methods=['GET'])
def get_project_statistics(project_id):
    """获取项目统计信息"""
    try:
        project = EdgeAIProject.query.get_or_404(project_id)
        
        statistics = project.get_statistics()
        
        # 添加更多统计信息
        statistics.update({
            'project_id': project.id,
            'project_name': project.name,
            'project_status': project.status,
            'owner_name': project.owner.username if project.owner else None,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'training_duration': self._get_training_duration(project),
            'node_details': [node.to_dict() for node in project.edge_nodes[:10]]  # 限制返回数量
        })
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': statistics
        })
    
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取项目统计失败: {str(e)}'
        }), 500

def _get_training_duration(project):
    """计算训练持续时间"""
    if not project.started_at:
        return 0
    
    end_time = project.completed_at if project.completed_at else datetime.utcnow()
    return int((end_time - project.started_at).total_seconds())