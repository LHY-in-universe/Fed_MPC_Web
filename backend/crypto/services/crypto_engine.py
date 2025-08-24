"""
加密引擎服务
提供核心的加密解密功能
"""

import os
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import secrets

class CryptoEngine:
    """加密引擎核心类"""
    
    def __init__(self):
        self.backend = default_backend()
    
    def generate_symmetric_key(self, algorithm='aes', key_size=256):
        """生成对称密钥"""
        if algorithm.lower() == 'aes':
            if key_size not in [128, 192, 256]:
                raise ValueError("AES密钥长度必须是128、192或256位")
            return secrets.token_bytes(key_size // 8)
        else:
            raise ValueError(f"不支持的对称加密算法: {algorithm}")
    
    def encrypt_symmetric(self, data, key, algorithm='aes', mode='gcm'):
        """对称加密"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm.lower() == 'aes':
            return self._encrypt_aes(data, key, mode)
        else:
            raise ValueError(f"不支持的加密算法: {algorithm}")
    
    def decrypt_symmetric(self, encrypted_data, key, algorithm='aes', mode='gcm'):
        """对称解密"""
        if algorithm.lower() == 'aes':
            return self._decrypt_aes(encrypted_data, key, mode)
        else:
            raise ValueError(f"不支持的解密算法: {algorithm}")
    
    def _encrypt_aes(self, data, key, mode='gcm'):
        """AES加密"""
        if mode.lower() == 'gcm':
            # GCM模式 - 推荐用于新应用
            iv = secrets.token_bytes(12)  # GCM推荐96位IV
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            return {
                'algorithm': 'aes',
                'mode': 'gcm',
                'iv': base64.b64encode(iv).decode('utf-8'),
                'tag': base64.b64encode(encryptor.tag).decode('utf-8'),
                'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
            }
            
        elif mode.lower() == 'cbc':
            # CBC模式 - 兼容性好
            iv = secrets.token_bytes(16)  # AES块大小
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            
            # PKCS7填充
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            return {
                'algorithm': 'aes',
                'mode': 'cbc',
                'iv': base64.b64encode(iv).decode('utf-8'),
                'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
            }
        else:
            raise ValueError(f"不支持的AES模式: {mode}")
    
    def _decrypt_aes(self, encrypted_data, key, mode='gcm'):
        """AES解密"""
        if mode.lower() == 'gcm':
            iv = base64.b64decode(encrypted_data['iv'])
            tag = base64.b64decode(encrypted_data['tag'])
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=self.backend)
            decryptor = cipher.decryptor()
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext
            
        elif mode.lower() == 'cbc':
            iv = base64.b64decode(encrypted_data['iv'])
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # 移除PKCS7填充
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()
            
            return plaintext
        else:
            raise ValueError(f"不支持的AES模式: {mode}")
    
    def encrypt_asymmetric(self, data, public_key, algorithm='rsa'):
        """非对称加密"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm.lower() == 'rsa':
            return self._encrypt_rsa(data, public_key)
        else:
            raise ValueError(f"不支持的非对称加密算法: {algorithm}")
    
    def decrypt_asymmetric(self, encrypted_data, private_key, algorithm='rsa'):
        """非对称解密"""
        if algorithm.lower() == 'rsa':
            return self._decrypt_rsa(encrypted_data, private_key)
        else:
            raise ValueError(f"不支持的非对称解密算法: {algorithm}")
    
    def _encrypt_rsa(self, data, public_key):
        """RSA加密"""
        # RSA加密有长度限制，大数据需要分块或使用混合加密
        max_length = (public_key.key_size // 8) - 42  # OAEP填充的开销
        
        if len(data) <= max_length:
            # 单块加密
            ciphertext = public_key.encrypt(
                data,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return {
                'algorithm': 'rsa',
                'mode': 'oaep',
                'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
            }
        else:
            # 混合加密 - 用AES加密数据，用RSA加密AES密钥
            aes_key = self.generate_symmetric_key('aes', 256)
            
            # AES加密数据
            aes_encrypted = self.encrypt_symmetric(data, aes_key, 'aes', 'gcm')
            
            # RSA加密AES密钥
            encrypted_key = public_key.encrypt(
                aes_key,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return {
                'algorithm': 'rsa_hybrid',
                'encrypted_key': base64.b64encode(encrypted_key).decode('utf-8'),
                'encrypted_data': aes_encrypted
            }
    
    def _decrypt_rsa(self, encrypted_data, private_key):
        """RSA解密"""
        if encrypted_data.get('algorithm') == 'rsa':
            # 单块解密
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            
            plaintext = private_key.decrypt(
                ciphertext,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return plaintext
            
        elif encrypted_data.get('algorithm') == 'rsa_hybrid':
            # 混合解密
            encrypted_key = base64.b64decode(encrypted_data['encrypted_key'])
            
            # RSA解密AES密钥
            aes_key = private_key.decrypt(
                encrypted_key,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # AES解密数据
            plaintext = self.decrypt_symmetric(encrypted_data['encrypted_data'], aes_key, 'aes', 'gcm')
            
            return plaintext
        else:
            raise ValueError(f"未知的加密算法: {encrypted_data.get('algorithm')}")
    
    def derive_key_from_password(self, password, salt=None, length=32, iterations=100000):
        """从密码派生密钥"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        if salt is None:
            salt = secrets.token_bytes(16)
        elif isinstance(salt, str):
            salt = salt.encode('utf-8')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            iterations=iterations,
            backend=self.backend
        )
        
        key = kdf.derive(password)
        
        return {
            'key': key,
            'salt': salt,
            'iterations': iterations
        }
    
    def encrypt_with_password(self, data, password, algorithm='aes'):
        """使用密码加密数据"""
        # 从密码派生密钥
        key_info = self.derive_key_from_password(password)
        key = key_info['key']
        salt = key_info['salt']
        
        # 加密数据
        encrypted = self.encrypt_symmetric(data, key, algorithm)
        
        # 添加密钥派生信息
        encrypted['kdf'] = {
            'algorithm': 'pbkdf2',
            'hash': 'sha256',
            'salt': base64.b64encode(salt).decode('utf-8'),
            'iterations': key_info['iterations']
        }
        
        return encrypted
    
    def decrypt_with_password(self, encrypted_data, password, algorithm='aes'):
        """使用密码解密数据"""
        # 提取密钥派生信息
        kdf_info = encrypted_data.get('kdf')
        if not kdf_info:
            raise ValueError("缺少密钥派生信息")
        
        salt = base64.b64decode(kdf_info['salt'])
        iterations = kdf_info['iterations']
        
        # 从密码派生密钥
        key_info = self.derive_key_from_password(password, salt, iterations=iterations)
        key = key_info['key']
        
        # 解密数据
        return self.decrypt_symmetric(encrypted_data, key, algorithm)
    
    def generate_secure_random(self, length=32):
        """生成安全随机数"""
        return secrets.token_bytes(length)
    
    def generate_secure_token(self, length=32):
        """生成安全令牌（URL安全的base64）"""
        return secrets.token_urlsafe(length)
    
    def hash_data(self, data, algorithm='sha256'):
        """计算数据哈希"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm.lower() == 'sha256':
            digest = hashes.Hash(hashes.SHA256(), backend=self.backend)
        elif algorithm.lower() == 'sha384':
            digest = hashes.Hash(hashes.SHA384(), backend=self.backend)
        elif algorithm.lower() == 'sha512':
            digest = hashes.Hash(hashes.SHA512(), backend=self.backend)
        else:
            raise ValueError(f"不支持的哈希算法: {algorithm}")
        
        digest.update(data)
        return digest.finalize()
    
    def verify_integrity(self, data, hash_value, algorithm='sha256'):
        """验证数据完整性"""
        computed_hash = self.hash_data(data, algorithm)
        
        if isinstance(hash_value, str):
            hash_value = base64.b64decode(hash_value)
        
        return computed_hash == hash_value
    
    def create_encryption_context(self, algorithm='aes', mode='gcm', key_size=256):
        """创建加密上下文"""
        context = {
            'algorithm': algorithm,
            'mode': mode,
            'key_size': key_size,
            'created_at': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
        
        if algorithm.lower() == 'aes':
            context['key'] = base64.b64encode(
                self.generate_symmetric_key(algorithm, key_size)
            ).decode('utf-8')
        
        return context
    
    def serialize_encrypted_data(self, encrypted_data):
        """序列化加密数据"""
        return json.dumps(encrypted_data, indent=2)
    
    def deserialize_encrypted_data(self, serialized_data):
        """反序列化加密数据"""
        if isinstance(serialized_data, str):
            return json.loads(serialized_data)
        return serialized_data
    
    def estimate_encryption_time(self, data_size, algorithm='aes'):
        """估算加密时间"""
        # 基于经验值的估算（毫秒）
        if algorithm.lower() == 'aes':
            # AES大约每MB需要1-5毫秒
            return (data_size / (1024 * 1024)) * 3
        elif algorithm.lower() == 'rsa':
            # RSA加密时间与密钥大小和数据大小相关
            return (data_size / 1024) * 10
        else:
            return data_size / 10000  # 默认估算
    
    def get_supported_algorithms(self):
        """获取支持的算法列表"""
        return {
            'symmetric': {
                'aes': {
                    'key_sizes': [128, 192, 256],
                    'modes': ['gcm', 'cbc'],
                    'description': '高级加密标准'
                }
            },
            'asymmetric': {
                'rsa': {
                    'key_sizes': [2048, 3072, 4096],
                    'description': 'RSA公钥加密'
                }
            },
            'hash': {
                'sha256': {'description': 'SHA-256哈希算法'},
                'sha384': {'description': 'SHA-384哈希算法'},
                'sha512': {'description': 'SHA-512哈希算法'}
            }
        }

# 全局加密引擎实例
crypto_engine = CryptoEngine()