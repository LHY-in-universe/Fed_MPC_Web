"""
AI模块数据集管理相关路由
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
import uuid

from shared.middleware.auth import auth_required, business_type_required
from shared.utils.helpers import success_response, error_response, safe_int
from shared.utils.validators import (
    validate_request_data, validate_file_extension, validate_file_size
)
from shared.services.user_service import UserService
from models.dataset import Dataset
from models.base import db

datasets_bp = Blueprint('datasets', __name__)


@datasets_bp.route('/create', methods=['POST'])
@auth_required
@business_type_required(['ai'])
def create_dataset():
    """创建新数据集"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # 验证请求数据
        required_fields = ['name', 'data_type', 'description']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段')
        
        # 验证数据类型
        valid_data_types = ['image', 'text', 'tabular', 'audio', 'video', 'time_series']
        if data['data_type'] not in valid_data_types:
            return error_response('无效的数据类型')
        
        # 创建数据集
        dataset = Dataset(
            user_id=user_id,
            name=data['name'].strip(),
            description=data['description'].strip(),
            data_type=data['data_type'],
            file_path=data.get('file_path', ''),
            total_samples=data.get('total_samples', 0),
            feature_count=data.get('feature_count', 0),
            class_count=data.get('class_count', 0),
            status='created',
            metadata=data.get('metadata', {})
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        return success_response({
            'dataset_id': dataset.id,
            'name': dataset.name,
            'data_type': dataset.data_type,
            'status': dataset.status,
            'created_at': dataset.created_at.isoformat()
        }, '数据集创建成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'创建数据集失败: {str(e)}', 500)


@datasets_bp.route('/list', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def get_datasets():
    """获取用户数据集列表"""
    try:
        user_id = session.get('user_id')
        page = safe_int(request.args.get('page', 1), 1)
        per_page = safe_int(request.args.get('per_page', 10), 10)
        status = request.args.get('status')
        data_type = request.args.get('data_type')
        
        # 构建查询
        query = Dataset.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if data_type:
            query = query.filter_by(data_type=data_type)
        
        # 分页查询
        datasets = query.order_by(Dataset.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        datasets_data = []
        for dataset in datasets.items:
            datasets_data.append({
                'id': dataset.id,
                'name': dataset.name,
                'description': dataset.description,
                'data_type': dataset.data_type,
                'status': dataset.status,
                'total_samples': dataset.total_samples,
                'feature_count': dataset.feature_count,
                'class_count': dataset.class_count,
                'file_size': dataset.file_size,
                'created_at': dataset.created_at.isoformat(),
                'updated_at': dataset.updated_at.isoformat() if dataset.updated_at else None
            })
        
        return success_response({
            'datasets': datasets_data,
            'total': datasets.total,
            'pages': datasets.pages,
            'current_page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return error_response(f'获取数据集列表失败: {str(e)}', 500)


@datasets_bp.route('/<int:dataset_id>', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def get_dataset_detail(dataset_id):
    """获取数据集详情"""
    try:
        user_id = session.get('user_id')
        
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()
        if not dataset:
            return error_response('数据集不存在', 404)
        
        return success_response({
            'id': dataset.id,
            'name': dataset.name,
            'description': dataset.description,
            'data_type': dataset.data_type,
            'file_path': dataset.file_path,
            'status': dataset.status,
            'total_samples': dataset.total_samples,
            'feature_count': dataset.feature_count,
            'class_count': dataset.class_count,
            'file_size': dataset.file_size,
            'metadata': dataset.metadata,
            'created_at': dataset.created_at.isoformat(),
            'updated_at': dataset.updated_at.isoformat() if dataset.updated_at else None
        })
        
    except Exception as e:
        return error_response(f'获取数据集详情失败: {str(e)}', 500)


@datasets_bp.route('/<int:dataset_id>', methods=['PUT'])
@auth_required
@business_type_required(['ai'])
def update_dataset(dataset_id):
    """更新数据集信息"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()
        if not dataset:
            return error_response('数据集不存在', 404)
        
        # 更新数据集信息
        if 'name' in data:
            dataset.name = data['name'].strip()
        
        if 'description' in data:
            dataset.description = data['description'].strip()
        
        if 'status' in data and data['status'] in ['created', 'processing', 'ready', 'error']:
            dataset.status = data['status']
        
        if 'metadata' in data:
            dataset.metadata = data['metadata']
        
        dataset.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response({
            'id': dataset.id,
            'name': dataset.name,
            'description': dataset.description,
            'status': dataset.status,
            'updated_at': dataset.updated_at.isoformat()
        }, '数据集更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'更新数据集失败: {str(e)}', 500)


@datasets_bp.route('/<int:dataset_id>', methods=['DELETE'])
@auth_required
@business_type_required(['ai'])
def delete_dataset(dataset_id):
    """删除数据集"""
    try:
        user_id = session.get('user_id')
        
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()
        if not dataset:
            return error_response('数据集不存在', 404)
        
        if dataset.status == 'processing':
            return error_response('数据集正在处理中，无法删除')
        
        # 删除数据集
        db.session.delete(dataset)
        db.session.commit()
        
        return success_response(None, '数据集删除成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'删除数据集失败: {str(e)}', 500)


@datasets_bp.route('/upload', methods=['POST'])
@auth_required
@business_type_required(['ai'])
def upload_dataset():
    """上传数据集文件"""
    try:
        user_id = session.get('user_id')
        
        # 检查文件是否存在
        if 'file' not in request.files:
            return error_response('没有上传文件')
        
        file = request.files['file']
        if file.filename == '':
            return error_response('没有选择文件')
        
        # 验证文件扩展名
        allowed_extensions = ['csv', 'json', 'xlsx', 'parquet', 'txt']
        if not validate_file_extension(file.filename, allowed_extensions):
            return error_response('不支持的文件格式')
        
        # 验证文件大小 (100MB)
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 移动回文件开头
        
        if not validate_file_size(file_size, 100):
            return error_response('文件大小超过限制')
        
        # 生成文件路径
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"dataset_{user_id}_{uuid.uuid4().hex[:12]}.{file_extension}"
        file_path = f"/uploads/datasets/{filename}"
        
        # 这里应该保存文件到实际位置，暂时模拟
        # file.save(file_path)
        
        # 创建数据集记录
        dataset = Dataset(
            user_id=user_id,
            name=request.form.get('name', file.filename),
            description=request.form.get('description', ''),
            data_type=request.form.get('data_type', 'tabular'),
            file_path=file_path,
            total_samples=0,
            feature_count=0,
            class_count=0,
            file_size=file_size,
            status='processing'
        )
        
        db.session.add(dataset)
        db.session.commit()
        
        return success_response({
            'dataset_id': dataset.id,
            'name': dataset.name,
            'file_path': file_path,
            'status': 'processing',
            'file_size': file_size
        }, '数据集上传成功，正在处理中')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'上传数据集失败: {str(e)}', 500)


@datasets_bp.route('/<int:dataset_id>/analyze', methods=['POST'])
@auth_required
@business_type_required(['ai'])
def analyze_dataset(dataset_id):
    """分析数据集"""
    try:
        user_id = session.get('user_id')
        
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()
        if not dataset:
            return error_response('数据集不存在', 404)
        
        if dataset.status != 'ready':
            return error_response('数据集未准备就绪')
        
        # 模拟数据分析
        analysis_result = {
            'basic_stats': {
                'total_samples': dataset.total_samples or 1000,
                'feature_count': dataset.feature_count or 10,
                'class_count': dataset.class_count or 3,
                'missing_values': 25,
                'duplicate_rows': 5
            },
            'data_quality': {
                'completeness': 97.5,
                'consistency': 92.3,
                'accuracy': 94.8,
                'uniqueness': 99.5
            },
            'feature_analysis': {
                'numerical_features': 8,
                'categorical_features': 2,
                'datetime_features': 0,
                'text_features': 0
            },
            'class_distribution': {
                'class_0': {'count': 400, 'percentage': 40.0},
                'class_1': {'count': 350, 'percentage': 35.0},
                'class_2': {'count': 250, 'percentage': 25.0}
            },
            'recommendations': [
                {'type': 'data_cleaning', 'priority': 'high', 'description': '处理缺失值和重复数据'},
                {'type': 'feature_engineering', 'priority': 'medium', 'description': '考虑特征缩放和编码'},
                {'type': 'data_augmentation', 'priority': 'low', 'description': '增加少数类别的样本数量'}
            ],
            'analyzed_at': datetime.utcnow().isoformat()
        }
        
        # 更新数据集元数据
        dataset.metadata = {
            **(dataset.metadata or {}),
            'analysis_result': analysis_result
        }
        dataset.updated_at = datetime.utcnow()
        db.session.commit()
        
        return success_response(analysis_result, '数据集分析完成')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'分析数据集失败: {str(e)}', 500)


@datasets_bp.route('/<int:dataset_id>/preview', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def preview_dataset(dataset_id):
    """预览数据集"""
    try:
        user_id = session.get('user_id')
        limit = safe_int(request.args.get('limit', 10), 10)
        
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()
        if not dataset:
            return error_response('数据集不存在', 404)
        
        if dataset.status not in ['ready', 'processing']:
            return error_response('数据集无法预览')
        
        # 模拟数据预览
        if dataset.data_type == 'tabular':
            preview_data = {
                'columns': ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'target'],
                'data': [
                    [1.2, 3.4, 5.6, 7.8, 'class_a'],
                    [2.1, 4.3, 6.5, 8.7, 'class_b'],
                    [3.0, 5.2, 7.4, 9.6, 'class_a'],
                    [4.1, 6.3, 8.5, 10.7, 'class_c'],
                    [5.2, 7.4, 9.6, 11.8, 'class_b']
                ],
                'total_rows': dataset.total_samples or 1000,
                'showing_rows': min(limit, 5)
            }
        elif dataset.data_type == 'image':
            preview_data = {
                'sample_images': [
                    {'filename': 'image_001.jpg', 'class': 'cat', 'size': [224, 224, 3]},
                    {'filename': 'image_002.jpg', 'class': 'dog', 'size': [224, 224, 3]},
                    {'filename': 'image_003.jpg', 'class': 'cat', 'size': [224, 224, 3]}
                ],
                'total_images': dataset.total_samples or 5000,
                'showing_samples': min(limit, 3)
            }
        else:
            preview_data = {
                'message': f'预览功能暂不支持 {dataset.data_type} 类型数据',
                'total_samples': dataset.total_samples or 0
            }
        
        return success_response(preview_data)
        
    except Exception as e:
        return error_response(f'预览数据集失败: {str(e)}', 500)


@datasets_bp.route('/templates', methods=['GET'])
@auth_required
@business_type_required(['ai'])
def get_dataset_templates():
    """获取数据集模板列表"""
    try:
        templates = [
            {
                'id': 'image_classification',
                'name': '图像分类数据集',
                'description': '用于图像分类任务的标准数据集格式',
                'data_type': 'image',
                'structure': {
                    'format': '文件夹结构',
                    'organization': 'class_name/image_files',
                    'supported_formats': ['jpg', 'png', 'bmp'],
                    'requirements': ['图像尺寸统一', '类别文件夹命名清晰']
                }
            },
            {
                'id': 'tabular_classification',
                'name': '表格分类数据集',
                'description': '用于分类任务的结构化数据集',
                'data_type': 'tabular',
                'structure': {
                    'format': 'CSV/Excel',
                    'organization': 'rows=samples, columns=features',
                    'supported_formats': ['csv', 'xlsx', 'parquet'],
                    'requirements': ['包含目标列', '数值型特征', '分类标签清晰']
                }
            },
            {
                'id': 'time_series',
                'name': '时间序列数据集',
                'description': '用于时间序列预测的数据集',
                'data_type': 'time_series',
                'structure': {
                    'format': 'CSV',
                    'organization': 'timestamp, features, target',
                    'supported_formats': ['csv', 'json'],
                    'requirements': ['时间戳列', '按时间排序', '固定时间间隔']
                }
            },
            {
                'id': 'text_classification',
                'name': '文本分类数据集',
                'description': '用于文本分类任务的数据集',
                'data_type': 'text',
                'structure': {
                    'format': 'CSV/JSON',
                    'organization': 'text, label',
                    'supported_formats': ['csv', 'json', 'txt'],
                    'requirements': ['文本内容列', '标签列', 'UTF-8编码']
                }
            }
        ]
        
        # 应用过滤器
        data_type = request.args.get('data_type')
        if data_type:
            templates = [t for t in templates if t['data_type'] == data_type]
        
        return success_response({
            'templates': templates,
            'total': len(templates)
        })
        
    except Exception as e:
        return error_response(f'获取数据集模板失败: {str(e)}', 500)