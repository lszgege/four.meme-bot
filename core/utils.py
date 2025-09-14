#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Four.meme 机器人工具函数
"""

import os
import time
import json
import hashlib
import requests
from typing import Dict, Any, Optional, List
from eth_account import Account
from eth_account.messages import encode_defunct
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class APIUtils:
    """API 调用工具类"""
    
    @staticmethod
    def make_request(
        method: str, 
        url: str, 
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        timeout: int = 30,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        发送HTTP请求，支持重试
        
        Args:
            method: 请求方法 (GET, POST)
            url: 请求URL
            headers: 请求头
            data: 请求数据
            files: 文件数据
            timeout: 超时时间
            max_retries: 最大重试次数
            
        Returns:
            响应数据
        """
        headers = headers or {}
        
        for attempt in range(max_retries):
            try:
                if method.upper() == "POST":
                    if files:
                        response = requests.post(url, headers=headers, files=files, timeout=timeout)
                    else:
                        response = requests.post(url, headers=headers, json=data, timeout=timeout)
                else:
                    response = requests.get(url, headers=headers, params=data, timeout=timeout)
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)  # 重试前等待1秒


class CryptoUtils:
    """加密工具类"""
    
    @staticmethod
    def sign_message(private_key: str, message: str) -> str:
        """
        使用私钥签名消息
        
        Args:
            private_key: 私钥
            message: 待签名消息
            
        Returns:
            签名字符串
        """
        try:
            # 确保私钥格式正确
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
            
            # 编码消息
            message_hash = encode_defunct(text=message)
            
            # 使用私钥签名
            account = Account.from_key(private_key)
            signature = account.sign_message(message_hash)
            
            return signature.signature.hex()
            
        except Exception as e:
            logger.error(f"签名消息失败: {e}")
            raise
    
    @staticmethod
    def validate_wallet_address(address: str) -> bool:
        """
        验证钱包地址格式
        
        Args:
            address: 钱包地址
            
        Returns:
            地址是否有效
        """
        if not address or not isinstance(address, str):
            return False
            
        if not address.startswith("0x"):
            return False
            
        if len(address) != 42:
            return False
            
        try:
            int(address[2:], 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def get_wallet_address_from_private_key(private_key: str) -> str:
        """
        从私钥获取钱包地址
        
        Args:
            private_key: 私钥
            
        Returns:
            钱包地址
        """
        try:
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
                
            account = Account.from_key(private_key)
            return account.address
            
        except Exception as e:
            logger.error(f"从私钥获取地址失败: {e}")
            raise


class ImageUtils:
    """图片处理工具类"""
    
    @staticmethod
    def validate_image(image_path: str) -> bool:
        """
        验证图片文件
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            图片是否有效
        """
        if not os.path.exists(image_path):
            logger.error(f"图片文件不存在: {image_path}")
            return False
        
        # 检查文件扩展名
        _, ext = os.path.splitext(image_path.lower())
        supported_formats = [".jpeg", ".jpg", ".png", ".gif", ".bmp", ".webp"]
        
        if ext not in supported_formats:
            logger.error(f"不支持的图片格式: {ext}")
            return False
        
        # 检查文件大小 (限制为10MB)
        file_size = os.path.getsize(image_path)
        max_size = 10 * 1024 * 1024  # 10MB
        
        if file_size > max_size:
            logger.error(f"图片文件过大: {file_size / 1024 / 1024:.2f}MB > 10MB")
            return False
        
        # 尝试打开图片验证格式
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"图片格式验证失败: {e}")
            return False
    
    @staticmethod
    def optimize_image(input_path: str, output_path: str, max_size: tuple = (1024, 1024), quality: int = 85) -> bool:
        """
        优化图片大小和质量
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            max_size: 最大尺寸 (width, height)
            quality: 图片质量 (1-100)
            
        Returns:
            优化是否成功
        """
        try:
            with Image.open(input_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # 调整尺寸
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 保存优化后的图片
                img.save(output_path, "JPEG", quality=quality, optimize=True)
                
            logger.info(f"图片优化成功: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"图片优化失败: {e}")
            return False


class TokenUtils:
    """代币工具类"""
    
    @staticmethod
    def validate_token_config(config: Dict[str, Any]) -> List[str]:
        """
        验证代币配置
        
        Args:
            config: 代币配置
            
        Returns:
            错误信息列表
        """
        errors = []
        
        # 必填字段检查
        required_fields = ["name", "shortName", "desc"]
        for field in required_fields:
            if not config.get(field):
                errors.append(f"缺少必填字段: {field}")
        
        # 代币名称长度检查
        if config.get("name") and len(config["name"]) > 50:
            errors.append("代币名称不能超过50个字符")
        
        # 代币符号长度检查
        if config.get("shortName") and len(config["shortName"]) > 10:
            errors.append("代币符号不能超过10个字符")
        
        # 描述长度检查
        if config.get("desc") and len(config["desc"]) > 500:
            errors.append("代币描述不能超过500个字符")
        
        # 分类检查
        supported_labels = ["Meme", "AI", "Defi", "Games", "Infra", "De-Sci", "Social", "Depin", "Charity", "Others"]
        if config.get("label") and config["label"] not in supported_labels:
            errors.append(f"不支持的代币分类: {config['label']}")
        
        # URL格式检查
        url_fields = ["webUrl", "twitterUrl", "telegramUrl"]
        for field in url_fields:
            url = config.get(field)
            if url and not url.startswith(("http://", "https://")):
                errors.append(f"{field} 必须以 http:// 或 https:// 开头")
        
        # 预售金额检查
        if config.get("preSale"):
            try:
                pre_sale = float(config["preSale"])
                if pre_sale < 0:
                    errors.append("预售金额不能为负数")
            except ValueError:
                errors.append("预售金额必须是有效数字")
        
        return errors
    
    @staticmethod
    def generate_token_config_template() -> Dict[str, Any]:
        """
        生成代币配置模板
        
        Returns:
            代币配置模板
        """
        return {
            "name": "示例代币",
            "shortName": "DEMO",
            "desc": "这是一个示例代币，用于演示创建流程",
            "label": "Meme",
            "webUrl": "https://example.com",
            "twitterUrl": "https://x.com/example",
            "telegramUrl": "https://t.me/example",
            "preSale": "0"
        }


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str) -> bool:
        """
        保存JSON数据到文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            
        Returns:
            保存是否成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Optional[Dict[str, Any]]:
        """
        从文件加载JSON数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            加载的数据，失败时返回None
        """
        try:
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载JSON文件失败: {e}")
            return None
    
    @staticmethod
    def ensure_directory(dir_path: str) -> bool:
        """
        确保目录存在，不存在则创建
        
        Args:
            dir_path: 目录路径
            
        Returns:
            目录是否存在或创建成功
        """
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"创建目录失败: {e}")
            return False


# 常用常量
SUPPORTED_NETWORKS = ["BSC", "ETH", "POLYGON"]
DEFAULT_GAS_LIMIT = 21000
DEFAULT_GAS_PRICE = 20  # Gwei

if __name__ == "__main__":
    # 测试工具函数
    print("测试工具函数...")
    
    # 测试钱包地址验证
    test_address = "0x742d35Cc6634C0532925a3b8D8C90F31e7C4dA3f"
    print(f"地址验证: {CryptoUtils.validate_wallet_address(test_address)}")
    
    # 测试代币配置验证
    test_config = TokenUtils.generate_token_config_template()
    errors = TokenUtils.validate_token_config(test_config)
    print(f"配置验证错误: {errors}")
    
    print("工具函数测试完成") 