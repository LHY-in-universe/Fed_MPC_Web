"""
AI模块项目管理相关路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

projects_bp = Blueprint('projects', __name__)

def success_response(data, message="Success"):
    """简单成功响应"""
    return jsonify({
        'success': True,
        'message': message,
        'data': data
    }), 200

def error_response(message, status_code=400):
    """简单错误响应"""
    return jsonify({
        'success': False,
        'error': message
    }), status_code

@projects_bp.route('/', methods=['GET'])
def get_projects():
    """获取项目列表"""
    try:
        # Mock project data
        projects = [
            {
                'id': str(uuid.uuid4()),
                'name': '联邦学习项目1',
                'type': 'image_classification',
                'status': 'active',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'name': '联邦学习项目2',
                'type': 'text_classification',
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        return success_response(projects)
        
    except Exception as e:
        return error_response(f'获取项目列表失败: {str(e)}', 500)

@projects_bp.route('/', methods=['POST'])
def create_project():
    """创建新项目"""
    try:
        data = request.get_json()
        project_id = str(uuid.uuid4())
        
        project = {
            'id': project_id,
            'name': data.get('name', '新项目'),
            'type': data.get('type', 'general'),
            'status': 'created',
            'created_at': datetime.now().isoformat()
        }
        
        return success_response(project, '项目创建成功')
        
    except Exception as e:
        return error_response(f'创建项目失败: {str(e)}', 500)

@projects_bp.route('/<project_id>', methods=['GET'])
def get_project(project_id):
    """获取项目详情"""
    try:
        project = {
            'id': project_id,
            'name': '联邦学习项目详情',
            'type': 'image_classification',
            'status': 'active',
            'participants': 3,
            'rounds_completed': 5,
            'total_rounds': 10,
            'created_at': datetime.now().isoformat()
        }
        
        return success_response(project)
        
    except Exception as e:
        return error_response(f'获取项目详情失败: {str(e)}', 500)