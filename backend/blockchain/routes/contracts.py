"""
区块链智能合约管理路由
处理智能合约的部署、调用和管理
"""

from flask import Blueprint, request, jsonify, session
import logging
from datetime import datetime
import hashlib
from shared.middleware.auth import auth_required, business_type_required
from shared.utils.helpers import success_response, error_response
from models.user import User

contracts_bp = Blueprint('blockchain_contracts', __name__, url_prefix='/contracts')
logger = logging.getLogger(__name__)

# 区块链合约存储
BLOCKCHAIN_CONTRACTS = {}
CONTRACT_TEMPLATES = [
    {
        'id': 'federated_learning_contract',
        'name': '联邦学习智能合约',
        'description': '管理联邦学习过程的智能合约模板',
        'contract_type': 'federated_learning',
        'functions': [
            'initializeFederatedLearning',
            'submitModelUpdate',
            'aggregateModels',
            'distributeGlobalModel',
            'recordTrainingMetrics'
        ],
        'parameters': {
            'min_participants': 3,
            'max_participants': 10,
            'training_rounds': 100,
            'convergence_threshold': 0.01
        }
    },
    {
        'id': 'privacy_preserving_contract',
        'name': '隐私保护合约',
        'description': '基于MPC的隐私保护计算合约',
        'contract_type': 'privacy_protection',
        'functions': [
            'initializeSecretSharing',
            'submitEncryptedData',
            'performSecureComputation',
            'revealResult',
            'verifyIntegrity'
        ],
        'parameters': {
            'encryption_algorithm': 'Shamir',
            'threshold': 2,
            'max_shares': 5
        }
    },
    {
        'id': 'reputation_contract',
        'name': '信誉评估合约',
        'description': '参与方信誉评估和奖励分配合约',
        'contract_type': 'reputation',
        'functions': [
            'initializeReputation',
            'updateReputationScore',
            'calculateRewards',
            'distributeTokens',
            'penalizeParticipant'
        ],
        'parameters': {
            'initial_reputation': 100,
            'max_reputation': 1000,
            'reward_rate': 0.05
        }
    }
]

@contracts_bp.route('/templates', methods=['GET'])
@auth_required
@business_type_required(['blockchain'])
def get_contract_templates():
    """
    获取智能合约模板列表
    """
    try:
        contract_type = request.args.get('contract_type')
        
        templates = CONTRACT_TEMPLATES
        
        if contract_type:
            templates = [t for t in templates if t['contract_type'] == contract_type]
        
        return jsonify({
            'success': True,
            'templates': templates
        }), 200
        
    except Exception as e:
        logger.error(f'获取合约模板失败: {str(e)}')
        return jsonify({'error': '获取合约模板失败'}), 500

@contracts_bp.route('', methods=['POST'])
@auth_required
@business_type_required(['blockchain'])
def deploy_contract():
    """
    部署智能合约
    
    请求参数:
    - name: 合约名称
    - description: 合约描述
    - contract_type: 合约类型
    - template_id: 模板ID (可选)
    - contract_code: 合约代码 (可选)
    - parameters: 合约参数
    """
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        contract_type = data.get('contract_type', 'federated_learning')
        template_id = data.get('template_id')
        contract_code = data.get('contract_code', '')
        parameters = data.get('parameters', {})
        
        if not name:
            return jsonify({'error': '合约名称不能为空'}), 400
        
        # 如果使用模板，获取模板配置
        template_config = {}
        if template_id:
            template = next((t for t in CONTRACT_TEMPLATES if t['id'] == template_id), None)
            if template:
                template_config = template
                contract_type = template['contract_type']
                parameters = {**template['parameters'], **parameters}
        
        # 生成合约地址
        contract_address = generate_contract_address(name, current_user.id)
        
        # 创建区块链合约
        contract_id = f"blockchain_contract_{current_user.id}_{int(datetime.now().timestamp())}"
        
        blockchain_contract = {
            'id': contract_id,
            'name': name,
            'description': description,
            'contract_type': contract_type,
            'contract_address': contract_address,
            'owner_id': current_user.id,
            'status': 'deployed',
            'template_config': template_config,
            'contract_code': contract_code,
            'parameters': parameters,
            'business_type': 'blockchain',
            'deployment_tx': f"0x{hashlib.sha256(f'{contract_id}{datetime.now()}'.encode()).hexdigest()}",
            'gas_used': 2500000,
            'deployed_at': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'function_calls': [],
            'events': []
        }
        
        # 保存合约
        if current_user.id not in BLOCKCHAIN_CONTRACTS:
            BLOCKCHAIN_CONTRACTS[current_user.id] = []
        BLOCKCHAIN_CONTRACTS[current_user.id].append(blockchain_contract)
        
        # 添加部署事件
        deploy_event = {
            'event_type': 'ContractDeployed',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'contract_address': contract_address,
                'deployer': current_user.id,
                'gas_used': 2500000
            }
        }
        blockchain_contract['events'].append(deploy_event)
        
        logger.info(f'区块链合约部署成功: {name} (用户: {current_user.id})')
        
        return jsonify({
            'success': True,
            'contract': blockchain_contract
        }), 201
        
    except Exception as e:
        logger.error(f'部署区块链合约失败: {str(e)}')
        return jsonify({'error': '部署区块链合约失败'}), 500

@contracts_bp.route('', methods=['GET'])
@auth_required
@business_type_required(['blockchain'])
def get_contracts():
    """
    获取用户的智能合约列表
    """
    try:
        contract_type = request.args.get('contract_type')
        status = request.args.get('status')
        
        user_contracts = BLOCKCHAIN_CONTRACTS.get(current_user.id, [])
        
        # 应用过滤器
        filtered_contracts = user_contracts
        
        if contract_type:
            filtered_contracts = [c for c in filtered_contracts if c['contract_type'] == contract_type]
        
        if status:
            filtered_contracts = [c for c in filtered_contracts if c['status'] == status]
        
        # 如果没有合约，添加示例合约
        if len(user_contracts) == 0:
            example_contracts = [
                {
                    'id': 'example_contract_1',
                    'name': '银行间信用评估联邦学习',
                    'description': '多银行联合进行信用风险评估的智能合约',
                    'contract_type': 'federated_learning',
                    'contract_address': '0x1234567890abcdef1234567890abcdef12345678',
                    'status': 'active',
                    'participants_count': 4,
                    'training_rounds': 50,
                    'current_round': 25,
                    'deployed_at': '2024-01-15T10:00:00',
                    'business_type': 'blockchain'
                },
                {
                    'id': 'example_contract_2',
                    'name': '多方安全计算合约',
                    'description': '基于MPC的隐私保护计算合约',
                    'contract_type': 'privacy_protection',
                    'contract_address': '0xabcdef1234567890abcdef1234567890abcdef12',
                    'status': 'active',
                    'participants_count': 3,
                    'computation_tasks': 12,
                    'deployed_at': '2024-01-20T14:30:00',
                    'business_type': 'blockchain'
                }
            ]
            filtered_contracts = example_contracts
        
        return jsonify({
            'success': True,
            'contracts': filtered_contracts,
            'total': len(filtered_contracts)
        }), 200
        
    except Exception as e:
        logger.error(f'获取合约列表失败: {str(e)}')
        return jsonify({'error': '获取合约列表失败'}), 500

@contracts_bp.route('/<contract_id>', methods=['GET'])
@auth_required
@business_type_required(['blockchain'])
def get_contract_detail(contract_id):
    """
    获取智能合约详情
    """
    try:
        # 查找合约
        contract = None
        user_contracts = BLOCKCHAIN_CONTRACTS.get(current_user.id, [])
        
        for c in user_contracts:
            if c['id'] == contract_id:
                contract = c
                break
        
        # 处理示例合约
        if not contract and contract_id.startswith('example_contract_'):
            if contract_id == 'example_contract_1':
                contract = {
                    'id': 'example_contract_1',
                    'name': '银行间信用评估联邦学习',
                    'description': '多银行联合进行信用风险评估的智能合约',
                    'contract_type': 'federated_learning',
                    'contract_address': '0x1234567890abcdef1234567890abcdef12345678',
                    'status': 'active',
                    'owner_id': current_user.id,
                    'participants': [
                        {'name': '工商银行', 'address': '0xbank1...', 'status': 'active'},
                        {'name': '建设银行', 'address': '0xbank2...', 'status': 'active'},
                        {'name': '招商银行', 'address': '0xbank3...', 'status': 'active'},
                        {'name': '民生银行', 'address': '0xbank4...', 'status': 'active'}
                    ],
                    'parameters': {
                        'min_participants': 3,
                        'max_participants': 10,
                        'training_rounds': 100,
                        'current_round': 25,
                        'convergence_threshold': 0.01
                    },
                    'deployed_at': '2024-01-15T10:00:00',
                    'business_type': 'blockchain',
                    'function_calls': [
                        {'function': 'initializeFederatedLearning', 'caller': '0xbank1...', 'timestamp': '2024-01-15T10:05:00'},
                        {'function': 'submitModelUpdate', 'caller': '0xbank2...', 'timestamp': '2024-01-15T11:30:00'}
                    ],
                    'events': [
                        {'event_type': 'TrainingRoundCompleted', 'round': 25, 'timestamp': '2024-01-22T15:45:00'},
                        {'event_type': 'ModelAggregated', 'accuracy': 92.3, 'timestamp': '2024-01-22T15:46:00'}
                    ]
                }
        
        if not contract:
            return jsonify({'error': '合约不存在'}), 404
        
        return jsonify({
            'success': True,
            'contract': contract
        }), 200
        
    except Exception as e:
        logger.error(f'获取合约详情失败: {str(e)}')
        return jsonify({'error': '获取合约详情失败'}), 500

@contracts_bp.route('/<contract_id>/call', methods=['POST'])
@auth_required
@business_type_required(['blockchain'])
def call_contract_function(contract_id):
    """
    调用智能合约函数
    
    请求参数:
    - function_name: 函数名
    - parameters: 函数参数
    - gas_limit: Gas限制
    """
    try:
        data = request.get_json()
        
        function_name = data.get('function_name')
        parameters = data.get('parameters', {})
        gas_limit = data.get('gas_limit', 100000)
        
        if not function_name:
            return jsonify({'error': '函数名不能为空'}), 400
        
        # 查找合约
        contract = None
        user_contracts = BLOCKCHAIN_CONTRACTS.get(current_user.id, [])
        contract_index = -1
        
        for i, c in enumerate(user_contracts):
            if c['id'] == contract_id:
                contract = c
                contract_index = i
                break
        
        if not contract:
            return jsonify({'error': '合约不存在'}), 404
        
        # 生成交易哈希
        tx_hash = f"0x{hashlib.sha256(f'{contract_id}{function_name}{datetime.now()}'.encode()).hexdigest()}"
        
        # 记录函数调用
        function_call = {
            'function': function_name,
            'parameters': parameters,
            'caller': current_user.id,
            'tx_hash': tx_hash,
            'gas_used': min(gas_limit, 80000),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        contract['function_calls'].append(function_call)
        
        # 模拟函数执行结果
        execution_result = simulate_contract_execution(function_name, parameters)
        
        # 添加事件日志
        if execution_result.get('event'):
            event_log = {
                'event_type': execution_result['event'],
                'data': execution_result.get('event_data', {}),
                'tx_hash': tx_hash,
                'timestamp': datetime.now().isoformat()
            }
            contract['events'].append(event_log)
        
        contract['updated_at'] = datetime.now().isoformat()
        
        # 保存更新
        BLOCKCHAIN_CONTRACTS[current_user.id][contract_index] = contract
        
        logger.info(f'合约函数调用成功: {function_name} (合约: {contract_id})')
        
        return jsonify({
            'success': True,
            'tx_hash': tx_hash,
            'gas_used': function_call['gas_used'],
            'result': execution_result.get('result'),
            'events': execution_result.get('events', [])
        }), 200
        
    except Exception as e:
        logger.error(f'调用合约函数失败: {str(e)}')
        return jsonify({'error': '调用合约函数失败'}), 500

@contracts_bp.route('/<contract_id>/events', methods=['GET'])
@auth_required
@business_type_required(['blockchain'])
def get_contract_events(contract_id):
    """
    获取智能合约事件日志
    """
    try:
        # 查找合约
        contract = None
        user_contracts = BLOCKCHAIN_CONTRACTS.get(current_user.id, [])
        
        for c in user_contracts:
            if c['id'] == contract_id:
                contract = c
                break
        
        if not contract:
            return jsonify({'error': '合约不存在'}), 404
        
        # 分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        event_type = request.args.get('event_type')
        
        events = contract.get('events', [])
        
        # 过滤事件类型
        if event_type:
            events = [e for e in events if e.get('event_type') == event_type]
        
        # 按时间倒序排列
        events = sorted(events, key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # 分页
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_events = events[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'events': paginated_events,
            'total': len(events),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(events) + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        logger.error(f'获取合约事件失败: {str(e)}')
        return jsonify({'error': '获取合约事件失败'}), 500

def generate_contract_address(name, user_id):
    """生成合约地址"""
    content = f"{name}_{user_id}_{datetime.now().timestamp()}"
    hash_object = hashlib.sha256(content.encode())
    return f"0x{hash_object.hexdigest()[:40]}"

def simulate_contract_execution(function_name, parameters):
    """模拟合约函数执行"""
    import random
    
    if function_name == 'initializeFederatedLearning':
        return {
            'result': {'status': 'initialized', 'participants': []},
            'event': 'FederatedLearningInitialized',
            'event_data': {'min_participants': parameters.get('min_participants', 3)}
        }
    
    elif function_name == 'submitModelUpdate':
        return {
            'result': {'status': 'accepted', 'update_hash': f"0x{hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]}"},
            'event': 'ModelUpdateSubmitted',
            'event_data': {'participant': parameters.get('participant', 'unknown')}
        }
    
    elif function_name == 'aggregateModels':
        return {
            'result': {
                'status': 'aggregated',
                'global_accuracy': round(random.uniform(0.85, 0.95), 4),
                'participants_count': random.randint(3, 8)
            },
            'event': 'ModelAggregated',
            'event_data': {'round': parameters.get('round', 1)}
        }
    
    elif function_name == 'performSecureComputation':
        return {
            'result': {
                'status': 'computed',
                'computation_id': f"comp_{random.randint(1000, 9999)}",
                'encrypted_result': f"enc_{hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]}"
            },
            'event': 'SecureComputationCompleted',
            'event_data': {'computation_type': parameters.get('computation_type', 'unknown')}
        }
    
    else:
        return {
            'result': {'status': 'executed'},
            'event': 'FunctionExecuted',
            'event_data': {'function': function_name}
        }