"""
区块链交易管理路由
处理区块链交易的创建、查询和监控
"""

from flask import Blueprint, request, jsonify, session
import logging
from datetime import datetime, timedelta
import hashlib
import random
from shared.middleware.auth import auth_required, business_type_required
from shared.utils.helpers import success_response, error_response, safe_int
from shared.utils.validators import validate_request_data

transactions_bp = Blueprint('blockchain_transactions', __name__, url_prefix='/transactions')
logger = logging.getLogger(__name__)

# 区块链交易存储
BLOCKCHAIN_TRANSACTIONS = {}
TRANSACTION_POOL = []

@transactions_bp.route('', methods=['POST'])
@auth_required
@business_type_required(['blockchain'])
def create_transaction():
    """
    创建区块链交易
    
    请求参数:
    - transaction_type: 交易类型 (transfer/contract_call/data_submission)
    - to_address: 目标地址
    - value: 交易金额 (可选)
    - data: 交易数据
    - gas_limit: Gas限制
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # 验证必填字段
        required_fields = ['to_address']
        if not validate_request_data(data, required_fields):
            return error_response('缺少必填字段: to_address')
        
        transaction_type = data.get('transaction_type', 'transfer')
        to_address = data.get('to_address')
        value = data.get('value', 0)
        tx_data = data.get('data', {})
        gas_limit = data.get('gas_limit', 21000)
        
        # 生成交易哈希
        tx_content = f"{user_id}_{to_address}_{transaction_type}_{datetime.now().timestamp()}"
        tx_hash = f"0x{hashlib.sha256(tx_content.encode()).hexdigest()}"
        
        # 创建区块链交易
        blockchain_transaction = {
            'tx_hash': tx_hash,
            'transaction_type': transaction_type,
            'from_address': f"0x{hashlib.sha256(str(user_id).encode()).hexdigest()[:40]}",
            'to_address': to_address,
            'value': value,
            'data': tx_data,
            'gas_limit': gas_limit,
            'gas_used': 0,
            'gas_price': 20,  # Gwei
            'nonce': get_user_nonce(user_id),
            'status': 'pending',
            'block_number': None,
            'block_hash': None,
            'transaction_index': None,
            'confirmations': 0,
            'created_at': datetime.now().isoformat(),
            'submitted_at': datetime.now().isoformat(),
            'confirmed_at': None,
            'owner_id': user_id,
            'business_type': 'blockchain'
        }
        
        # 添加到交易池
        TRANSACTION_POOL.append(blockchain_transaction)
        
        # 保存交易
        if user_id not in BLOCKCHAIN_TRANSACTIONS:
            BLOCKCHAIN_TRANSACTIONS[user_id] = []
        BLOCKCHAIN_TRANSACTIONS[user_id].append(blockchain_transaction)
        
        logger.info(f'区块链交易创建成功: {tx_hash} (用户: {user_id})')
        
        return success_response(blockchain_transaction, '区块链交易创建成功')
        
    except Exception as e:
        logger.error(f'创建区块链交易失败: {str(e)}')
        return error_response(f'创建区块链交易失败: {str(e)}', 500)

@transactions_bp.route('', methods=['GET'])
@auth_required
@business_type_required(['blockchain'])
def get_transactions():
    """
    获取用户的区块链交易列表
    """
    try:
        status = request.args.get('status')
        transaction_type = request.args.get('transaction_type')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        user_transactions = BLOCKCHAIN_TRANSACTIONS.get(user_id, [])
        
        # 应用过滤器
        filtered_transactions = user_transactions
        
        if status:
            filtered_transactions = [t for t in filtered_transactions if t['status'] == status]
        
        if transaction_type:
            filtered_transactions = [t for t in filtered_transactions if t['transaction_type'] == transaction_type]
        
        # 按时间倒序排列
        filtered_transactions = sorted(filtered_transactions, key=lambda x: x['created_at'], reverse=True)
        
        # 如果没有交易，添加示例交易
        if len(user_transactions) == 0:
            example_transactions = [
                {
                    'tx_hash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
                    'transaction_type': 'contract_call',
                    'from_address': f"0x{hashlib.sha256(str(user_id).encode()).hexdigest()[:40]}",
                    'to_address': '0x1234567890abcdef1234567890abcdef12345678',
                    'value': 0,
                    'gas_used': 85000,
                    'gas_price': 20,
                    'status': 'confirmed',
                    'block_number': 12345678,
                    'confirmations': 12,
                    'created_at': '2024-01-20T10:30:00',
                    'confirmed_at': '2024-01-20T10:31:00',
                    'business_type': 'blockchain'
                },
                {
                    'tx_hash': '0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890',
                    'transaction_type': 'data_submission',
                    'from_address': f"0x{hashlib.sha256(str(user_id).encode()).hexdigest()[:40]}",
                    'to_address': '0xabcdef1234567890abcdef1234567890abcdef12',
                    'value': 0,
                    'gas_used': 65000,
                    'gas_price': 22,
                    'status': 'confirmed',
                    'block_number': 12345690,
                    'confirmations': 8,
                    'created_at': '2024-01-22T14:15:00',
                    'confirmed_at': '2024-01-22T14:16:00',
                    'business_type': 'blockchain'
                }
            ]
            filtered_transactions = example_transactions
        
        # 分页
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_transactions = filtered_transactions[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'transactions': paginated_transactions,
            'total': len(filtered_transactions),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(filtered_transactions) + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        logger.error(f'获取交易列表失败: {str(e)}')
        return jsonify({'error': '获取交易列表失败'}), 500

@transactions_bp.route('/<tx_hash>', methods=['GET'])
@auth_required
@business_type_required(['blockchain'])
def get_transaction_detail(tx_hash):
    """
    获取区块链交易详情
    """
    try:
        # 查找交易
        transaction = None
        user_transactions = BLOCKCHAIN_TRANSACTIONS.get(user_id, [])
        
        for t in user_transactions:
            if t['tx_hash'] == tx_hash:
                transaction = t
                break
        
        # 处理示例交易
        if not transaction and tx_hash.startswith('0x'):
            transaction = {
                'tx_hash': tx_hash,
                'transaction_type': 'contract_call',
                'from_address': f"0x{hashlib.sha256(str(user_id).encode()).hexdigest()[:40]}",
                'to_address': '0x1234567890abcdef1234567890abcdef12345678',
                'value': 0,
                'data': {
                    'function': 'submitModelUpdate',
                    'parameters': {
                        'model_hash': '0xmodel123...',
                        'accuracy': 0.923
                    }
                },
                'gas_limit': 100000,
                'gas_used': 85000,
                'gas_price': 20,
                'nonce': 42,
                'status': 'confirmed',
                'block_number': 12345678,
                'block_hash': '0xblock123...',
                'transaction_index': 15,
                'confirmations': 12,
                'created_at': '2024-01-20T10:30:00',
                'submitted_at': '2024-01-20T10:30:05',
                'confirmed_at': '2024-01-20T10:31:00',
                'business_type': 'blockchain',
                'logs': [
                    {
                        'address': '0x1234567890abcdef1234567890abcdef12345678',
                        'topics': ['0xModelUpdateSubmitted'],
                        'data': '0xparticipant_data...'
                    }
                ]
            }
        
        if not transaction:
            return jsonify({'error': '交易不存在'}), 404
        
        return jsonify({
            'success': True,
            'transaction': transaction
        }), 200
        
    except Exception as e:
        logger.error(f'获取交易详情失败: {str(e)}')
        return jsonify({'error': '获取交易详情失败'}), 500

@transactions_bp.route('/<tx_hash>/status', methods=['GET'])
@auth_required
@business_type_required(['blockchain'])
def get_transaction_status(tx_hash):
    """
    获取交易状态
    """
    try:
        # 查找交易
        transaction = None
        user_transactions = BLOCKCHAIN_TRANSACTIONS.get(user_id, [])
        
        for t in user_transactions:
            if t['tx_hash'] == tx_hash:
                transaction = t
                break
        
        if not transaction:
            return jsonify({'error': '交易不存在'}), 404
        
        # 模拟交易状态更新
        if transaction['status'] == 'pending':
            # 模拟一定概率的交易确认
            if random.random() < 0.7:  # 70%概率已确认
                transaction['status'] = 'confirmed'
                transaction['block_number'] = random.randint(12340000, 12350000)
                transaction['block_hash'] = f"0x{hashlib.sha256(str(random.random()).encode()).hexdigest()}"
                transaction['transaction_index'] = random.randint(0, 100)
                transaction['confirmations'] = random.randint(1, 20)
                transaction['confirmed_at'] = datetime.now().isoformat()
                transaction['gas_used'] = min(transaction['gas_limit'], random.randint(20000, transaction['gas_limit']))
        
        status_info = {
            'tx_hash': tx_hash,
            'status': transaction['status'],
            'confirmations': transaction['confirmations'],
            'block_number': transaction['block_number'],
            'gas_used': transaction['gas_used'],
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'status': status_info
        }), 200
        
    except Exception as e:
        logger.error(f'获取交易状态失败: {str(e)}')
        return jsonify({'error': '获取交易状态失败'}), 500

@transactions_bp.route('/pool', methods=['GET'])
@auth_required
@business_type_required(['blockchain'])
def get_transaction_pool():
    """
    获取交易池状态
    """
    try:
        # 过滤待处理交易
        pending_transactions = [t for t in TRANSACTION_POOL if t['status'] == 'pending']
        
        # 按gas价格排序
        pending_transactions = sorted(pending_transactions, key=lambda x: x['gas_price'], reverse=True)
        
        pool_info = {
            'total_pending': len(pending_transactions),
            'average_gas_price': sum([t['gas_price'] for t in pending_transactions]) / len(pending_transactions) if pending_transactions else 0,
            'oldest_transaction': min([t['created_at'] for t in pending_transactions]) if pending_transactions else None,
            'transactions': pending_transactions[:10]  # 返回前10个交易
        }
        
        return jsonify({
            'success': True,
            'pool_info': pool_info
        }), 200
        
    except Exception as e:
        logger.error(f'获取交易池失败: {str(e)}')
        return jsonify({'error': '获取交易池失败'}), 500

@transactions_bp.route('/statistics', methods=['GET'])
@auth_required
@business_type_required(['blockchain'])
def get_transaction_statistics():
    """
    获取交易统计信息
    """
    try:
        # 获取用户交易
        user_transactions = BLOCKCHAIN_TRANSACTIONS.get(user_id, [])
        
        # 计算统计数据
        total_transactions = len(user_transactions)
        confirmed_transactions = len([t for t in user_transactions if t['status'] == 'confirmed'])
        pending_transactions = len([t for t in user_transactions if t['status'] == 'pending'])
        failed_transactions = len([t for t in user_transactions if t['status'] == 'failed'])
        
        # 按类型分组
        type_distribution = {}
        for tx in user_transactions:
            tx_type = tx['transaction_type']
            type_distribution[tx_type] = type_distribution.get(tx_type, 0) + 1
        
        # 计算Gas使用统计
        total_gas_used = sum([t.get('gas_used', 0) for t in user_transactions if t['status'] == 'confirmed'])
        average_gas_price = sum([t['gas_price'] for t in user_transactions]) / total_transactions if total_transactions else 0
        
        # 最近24小时交易数量
        yesterday = datetime.now() - timedelta(days=1)
        recent_transactions = [t for t in user_transactions if datetime.fromisoformat(t['created_at'].replace('Z', '+00:00')) > yesterday]
        
        statistics = {
            'total_transactions': total_transactions,
            'confirmed_transactions': confirmed_transactions,
            'pending_transactions': pending_transactions,
            'failed_transactions': failed_transactions,
            'success_rate': (confirmed_transactions / total_transactions * 100) if total_transactions > 0 else 0,
            'type_distribution': type_distribution,
            'total_gas_used': total_gas_used,
            'average_gas_price': round(average_gas_price, 2),
            'recent_24h_count': len(recent_transactions),
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        }), 200
        
    except Exception as e:
        logger.error(f'获取交易统计失败: {str(e)}')
        return jsonify({'error': '获取交易统计失败'}), 500

@transactions_bp.route('/estimate-gas', methods=['POST'])
@auth_required
@business_type_required(['blockchain'])
def estimate_gas():
    """
    估算交易Gas费用
    
    请求参数:
    - transaction_type: 交易类型
    - to_address: 目标地址
    - data: 交易数据
    """
    try:
        data = request.get_json()
        
        transaction_type = data.get('transaction_type', 'transfer')
        to_address = data.get('to_address')
        tx_data = data.get('data', {})
        
        # 估算Gas使用量
        gas_estimates = {
            'transfer': 21000,
            'contract_call': random.randint(50000, 150000),
            'data_submission': random.randint(30000, 100000),
            'contract_deployment': random.randint(200000, 500000)
        }
        
        estimated_gas = gas_estimates.get(transaction_type, 50000)
        
        # 考虑数据大小
        if tx_data:
            data_size = len(str(tx_data))
            estimated_gas += data_size * 16  # 每字节数据消耗16 gas
        
        # 获取当前Gas价格
        current_gas_price = random.randint(15, 30)  # Gwei
        
        estimate_result = {
            'estimated_gas': estimated_gas,
            'gas_price': current_gas_price,
            'estimated_cost': estimated_gas * current_gas_price,  # wei
            'estimated_cost_eth': (estimated_gas * current_gas_price) / (10**9),  # ETH
            'transaction_type': transaction_type,
            'estimated_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'estimate': estimate_result
        }), 200
        
    except Exception as e:
        logger.error(f'估算Gas费用失败: {str(e)}')
        return jsonify({'error': '估算Gas费用失败'}), 500

def get_user_nonce(user_id):
    """获取用户nonce"""
    user_transactions = BLOCKCHAIN_TRANSACTIONS.get(user_id, [])
    confirmed_transactions = [t for t in user_transactions if t['status'] == 'confirmed']
    return len(confirmed_transactions)