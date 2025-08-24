"""
密钥管理服务
提供密钥生命周期管理功能
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ..models.key_pair import KeyPair, KeyType, KeyUsage, KeyStatus
from ..models.certificate import Certificate
from .crypto_engine import crypto_engine

logger = logging.getLogger(__name__)

class KeyManager:
    """密钥管理器"""
    
    def __init__(self):
        self.crypto_engine = crypto_engine
    
    def create_key_pair(self, user_id: int, name: str, key_type: str = 'rsa', 
                       key_size: int = 2048, key_usage: str = 'both', 
                       passphrase: Optional[str] = None, **kwargs) -> KeyPair:
        """创建新密钥对"""
        try:
            # 验证参数
            self._validate_key_parameters(key_type, key_size, key_usage)
            
            # 创建密钥对实例
            key_pair = KeyPair.create_key_pair(
                user_id=user_id,
                name=name,
                key_type=key_type,
                key_size=key_size,
                key_usage=key_usage,
                passphrase=passphrase,
                **kwargs
            )
            
            logger.info(f"成功创建密钥对: {key_pair.key_id} for user {user_id}")
            return key_pair
            
        except Exception as e:
            logger.error(f"创建密钥对失败: {str(e)}")
            raise
    
    def get_user_keys(self, user_id: int, status: Optional[str] = None, 
                     key_type: Optional[str] = None) -> List[KeyPair]:
        """获取用户的密钥列表"""
        try:
            status_enum = KeyStatus(status) if status else None
            type_enum = KeyType(key_type) if key_type else None
            
            return KeyPair.get_user_keys(user_id, status_enum, type_enum)
            
        except Exception as e:
            logger.error(f"获取用户密钥失败: {str(e)}")
            raise
    
    def get_key_by_id(self, key_id: str, user_id: Optional[int] = None) -> Optional[KeyPair]:
        """根据ID获取密钥"""
        try:
            key_pair = KeyPair.get_by_key_id(key_id)
            
            # 权限检查
            if user_id and key_pair and key_pair.user_id != user_id:
                logger.warning(f"用户 {user_id} 尝试访问不属于自己的密钥 {key_id}")
                return None
            
            return key_pair
            
        except Exception as e:
            logger.error(f"获取密钥失败: {str(e)}")
            raise
    
    def export_public_key(self, key_id: str, format: str = 'PEM', 
                         user_id: Optional[int] = None) -> str:
        """导出公钥"""
        try:
            key_pair = self.get_key_by_id(key_id, user_id)
            if not key_pair:
                raise ValueError("密钥不存在或无权限访问")
            
            # 更新使用统计
            key_pair.update_usage()
            
            return key_pair.export_public_key(format)
            
        except Exception as e:
            logger.error(f"导出公钥失败: {str(e)}")
            raise
    
    def revoke_key(self, key_id: str, reason: str, user_id: Optional[int] = None) -> bool:
        """吊销密钥"""
        try:
            key_pair = self.get_key_by_id(key_id, user_id)
            if not key_pair:
                raise ValueError("密钥不存在或无权限访问")
            
            if key_pair.status != KeyStatus.ACTIVE:
                raise ValueError("只能吊销活跃状态的密钥")
            
            key_pair.revoke(reason)
            
            logger.info(f"密钥 {key_id} 已被吊销，原因: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"吊销密钥失败: {str(e)}")
            raise
    
    def archive_key(self, key_id: str, user_id: Optional[int] = None) -> bool:
        """归档密钥"""
        try:
            key_pair = self.get_key_by_id(key_id, user_id)
            if not key_pair:
                raise ValueError("密钥不存在或无权限访问")
            
            if key_pair.status == KeyStatus.ACTIVE:
                raise ValueError("活跃密钥需要先吊销才能归档")
            
            key_pair.archive()
            
            logger.info(f"密钥 {key_id} 已归档")
            return True
            
        except Exception as e:
            logger.error(f"归档密钥失败: {str(e)}")
            raise
    
    def extend_key_expiry(self, key_id: str, days: int = 365, 
                         user_id: Optional[int] = None) -> bool:
        """延长密钥过期时间"""
        try:
            key_pair = self.get_key_by_id(key_id, user_id)
            if not key_pair:
                raise ValueError("密钥不存在或无权限访问")
            
            if key_pair.status != KeyStatus.ACTIVE:
                raise ValueError("只能延长活跃密钥的过期时间")
            
            key_pair.extend_expiry(days)
            
            logger.info(f"密钥 {key_id} 过期时间已延长 {days} 天")
            return True
            
        except Exception as e:
            logger.error(f"延长密钥过期时间失败: {str(e)}")
            raise
    
    def get_expiring_keys(self, days: int = 30, user_id: Optional[int] = None) -> List[KeyPair]:
        """获取即将过期的密钥"""
        try:
            expiry_threshold = datetime.utcnow() + timedelta(days=days)
            
            from ..models.key_pair import db
            query = KeyPair.query.filter(
                KeyPair.expires_at <= expiry_threshold,
                KeyPair.status == KeyStatus.ACTIVE
            )
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"获取即将过期密钥失败: {str(e)}")
            raise
    
    def validate_key_passphrase(self, key_id: str, passphrase: str, 
                               user_id: Optional[int] = None) -> bool:
        """验证密钥密码"""
        try:
            key_pair = self.get_key_by_id(key_id, user_id)
            if not key_pair:
                raise ValueError("密钥不存在或无权限访问")
            
            return key_pair.verify_passphrase(passphrase)
            
        except Exception as e:
            logger.error(f"验证密钥密码失败: {str(e)}")
            return False
    
    def get_key_usage_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """获取密钥使用统计"""
        try:
            from ..models.key_pair import db
            from sqlalchemy import func
            
            query = db.session.query(
                KeyPair.key_type,
                KeyPair.status,
                func.count(KeyPair.id).label('count'),
                func.sum(KeyPair.usage_count).label('total_usage')
            )
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            results = query.group_by(KeyPair.key_type, KeyPair.status).all()
            
            statistics = {
                'total_keys': 0,
                'by_type': {},
                'by_status': {},
                'total_usage': 0
            }
            
            for result in results:
                key_type = result.key_type.value
                status = result.status.value
                count = result.count
                usage = result.total_usage or 0
                
                statistics['total_keys'] += count
                statistics['total_usage'] += usage
                
                if key_type not in statistics['by_type']:
                    statistics['by_type'][key_type] = 0
                statistics['by_type'][key_type] += count
                
                if status not in statistics['by_status']:
                    statistics['by_status'][status] = 0
                statistics['by_status'][status] += count
            
            return statistics
            
        except Exception as e:
            logger.error(f"获取密钥统计失败: {str(e)}")
            raise
    
    def cleanup_expired_keys(self) -> int:
        """清理过期密钥"""
        try:
            now = datetime.utcnow()
            
            # 查找过期但仍然活跃的密钥
            expired_keys = KeyPair.query.filter(
                KeyPair.expires_at < now,
                KeyPair.status == KeyStatus.ACTIVE
            ).all()
            
            count = 0
            for key_pair in expired_keys:
                key_pair.status = KeyStatus.EXPIRED
                key_pair.save()
                count += 1
                logger.info(f"密钥 {key_pair.key_id} 已自动标记为过期")
            
            return count
            
        except Exception as e:
            logger.error(f"清理过期密钥失败: {str(e)}")
            raise
    
    def generate_key_backup(self, key_id: str, passphrase: str, 
                           user_id: Optional[int] = None) -> Dict[str, Any]:
        """生成密钥备份"""
        try:
            key_pair = self.get_key_by_id(key_id, user_id)
            if not key_pair:
                raise ValueError("密钥不存在或无权限访问")
            
            if not key_pair.verify_passphrase(passphrase):
                raise ValueError("密码错误")
            
            backup_data = {
                'key_id': key_pair.key_id,
                'name': key_pair.name,
                'key_type': key_pair.key_type.value,
                'key_size': key_pair.key_size,
                'key_usage': key_pair.key_usage.value,
                'public_key': key_pair.public_key_pem,
                'fingerprint': key_pair.fingerprint,
                'created_at': key_pair.created_at.isoformat(),
                'backup_created_at': datetime.utcnow().isoformat(),
                'version': '1.0'
            }
            
            logger.info(f"生成密钥 {key_id} 的备份")
            return backup_data
            
        except Exception as e:
            logger.error(f"生成密钥备份失败: {str(e)}")
            raise
    
    def restore_key_from_backup(self, backup_data: Dict[str, Any], user_id: int, 
                               new_passphrase: Optional[str] = None) -> KeyPair:
        """从备份恢复密钥"""
        try:
            # 验证备份数据
            required_fields = ['key_id', 'name', 'key_type', 'public_key', 'fingerprint']
            for field in required_fields:
                if field not in backup_data:
                    raise ValueError(f"备份数据缺少必需字段: {field}")
            
            # 检查密钥是否已存在
            existing_key = KeyPair.get_by_key_id(backup_data['key_id'])
            if existing_key:
                raise ValueError("密钥已存在，无法恢复")
            
            # 创建新密钥对实例
            key_pair = KeyPair(
                user_id=user_id,
                name=backup_data['name'],
                key_type=backup_data['key_type'],
                key_size=backup_data.get('key_size', 2048),
                key_usage=backup_data.get('key_usage', 'both')
            )
            
            # 设置恢复的属性
            key_pair.key_id = backup_data['key_id']
            key_pair.public_key_pem = backup_data['public_key']
            key_pair.fingerprint = backup_data['fingerprint']
            
            # 注意：私钥无法从备份恢复，需要用户重新导入
            key_pair.private_key_encrypted = ''
            key_pair.salt = ''
            
            key_pair.save()
            
            logger.info(f"从备份恢复密钥 {key_pair.key_id}")
            return key_pair
            
        except Exception as e:
            logger.error(f"从备份恢复密钥失败: {str(e)}")
            raise
    
    def _validate_key_parameters(self, key_type: str, key_size: int, key_usage: str):
        """验证密钥参数"""
        # 验证密钥类型
        try:
            KeyType(key_type)
        except ValueError:
            raise ValueError(f"不支持的密钥类型: {key_type}")
        
        # 验证密钥用途
        try:
            KeyUsage(key_usage)
        except ValueError:
            raise ValueError(f"不支持的密钥用途: {key_usage}")
        
        # 验证密钥大小
        if key_type.lower() == 'rsa':
            if key_size not in [1024, 2048, 3072, 4096]:
                raise ValueError("RSA密钥大小必须是1024、2048、3072或4096位")
        elif key_type.lower() == 'ecc':
            if key_size not in [256, 384, 521]:
                raise ValueError("ECC密钥大小必须是256、384或521位")
    
    def get_key_recommendations(self, user_id: int) -> Dict[str, Any]:
        """获取密钥管理建议"""
        try:
            user_keys = self.get_user_keys(user_id)
            expiring_keys = self.get_expiring_keys(30, user_id)
            
            recommendations = {
                'total_keys': len(user_keys),
                'expiring_soon': len(expiring_keys),
                'suggestions': []
            }
            
            # 检查是否有密钥
            if len(user_keys) == 0:
                recommendations['suggestions'].append({
                    'type': 'create_first_key',
                    'priority': 'high',
                    'message': '建议创建您的第一个密钥对'
                })
            
            # 检查即将过期的密钥
            if len(expiring_keys) > 0:
                recommendations['suggestions'].append({
                    'type': 'expiring_keys',
                    'priority': 'medium',
                    'message': f'有 {len(expiring_keys)} 个密钥即将过期，建议及时更新'
                })
            
            # 检查密钥类型分布
            rsa_keys = [k for k in user_keys if k.key_type == KeyType.RSA]
            ecc_keys = [k for k in user_keys if k.key_type == KeyType.ECC]
            
            if len(rsa_keys) > 0 and len(ecc_keys) == 0:
                recommendations['suggestions'].append({
                    'type': 'diversify_key_types',
                    'priority': 'low',
                    'message': '建议添加ECC密钥以提高性能和安全性'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"获取密钥建议失败: {str(e)}")
            raise

# 全局密钥管理器实例
key_manager = KeyManager()