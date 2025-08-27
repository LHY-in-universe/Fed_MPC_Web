"""
AI模块数据集管理相关路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

datasets_bp = Blueprint('datasets', __name__)

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

@datasets_bp.route('/', methods=['GET'])
def get_datasets():
    """获取数据集列表"""
    try:
        datasets = [
            {
                'id': str(uuid.uuid4()),
                'name': 'MNIST',
                'type': 'image',
                'size': 70000,
                'status': 'ready',
                'created_at': datetime.now().isoformat()
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'CIFAR-10',
                'type': 'image',
                'size': 60000,
                'status': 'ready',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        return success_response(datasets)
        
    except Exception as e:
        return error_response(f'获取数据集列表失败: {str(e)}', 500)

@datasets_bp.route('/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """获取数据集详情"""
    try:
        dataset = {
            'id': dataset_id,
            'name': 'MNIST',
            'type': 'image',
            'size': 70000,
            'status': 'ready',
            'description': '手写数字识别数据集',
            'created_at': datetime.now().isoformat()
        }
        
        return success_response(dataset)
        
    except Exception as e:
        return error_response(f'获取数据集详情失败: {str(e)}', 500)

@datasets_bp.route('/upload', methods=['POST'])
def upload_dataset():
    """上传数据集"""
    try:
        # Mock upload response
        dataset_id = str(uuid.uuid4())
        
        return success_response({
            'dataset_id': dataset_id,
            'status': 'uploaded',
            'message': '数据集上传成功'
        })
        
    except Exception as e:
        return error_response(f'上传数据集失败: {str(e)}', 500)