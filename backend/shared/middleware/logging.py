"""
日志中间件
提供统一的请求日志记录和错误跟踪
"""

import logging
import os
from datetime import datetime
from flask import request, session, current_app


def setup_logging(app):
    """设置应用日志"""
    # 创建日志目录
    log_dir = os.path.join(app.root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f'fed_platform_{datetime.now().strftime("%Y-%m")}.log')
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 错误文件处理器
    error_handler = logging.FileHandler(
        os.path.join(log_dir, f'errors_{datetime.now().strftime("%Y-%m")}.log')
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # 添加处理器到应用
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)


def log_request():
    """记录请求信息"""
    if request.path.startswith('/api/'):
        user_id = session.get('user_id', 'anonymous')
        business_type = session.get('business_type', 'unknown')
        
        current_app.logger.info(
            f"API Request - User: {user_id} | Business: {business_type} | "
            f"Method: {request.method} | Path: {request.path} | "
            f"IP: {request.remote_addr} | UA: {request.headers.get('User-Agent', 'Unknown')}"
        )


def log_error(error, context=None):
    """记录错误信息"""
    user_id = session.get('user_id', 'anonymous')
    business_type = session.get('business_type', 'unknown')
    
    error_msg = (
        f"Error occurred - User: {user_id} | Business: {business_type} | "
        f"Path: {request.path} | Error: {str(error)}"
    )
    
    if context:
        error_msg += f" | Context: {context}"
    
    current_app.logger.error(error_msg, exc_info=True)