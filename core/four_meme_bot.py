#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Four.meme 代币创建机器人
支持自动登录、上传图片和创建代币
"""

import json
import time
import requests
from typing import Dict, Any, Optional
from eth_account import Account
from eth_account.messages import encode_defunct
import logging
from .blockchain_utils import BlockchainManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('four_meme_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FourMemeBot:
    """Four.meme 平台交互机器人"""
    
    def __init__(self, private_key: str, wallet_address: str, enable_blockchain: bool = True):
        """
        初始化机器人
        
        Args:
            private_key: 钱包私钥
            wallet_address: 钱包地址
            enable_blockchain: 是否启用区块链交互
        """
        self.private_key = private_key
        self.wallet_address = wallet_address
        self.access_token = None
        self.base_url = "https://four.meme/meme-api"
        self.session = requests.Session()
        self.blockchain_manager = None
        
        # 设置请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 初始化区块链管理器
        if enable_blockchain:
            try:
                self.blockchain_manager = BlockchainManager(private_key)
                logger.info("区块链管理器初始化成功")
            except Exception as e:
                logger.warning(f"区块链管理器初始化失败: {e}")
                self.blockchain_manager = None
    
    def generate_nonce(self) -> str:
        """
        生成登录用的随机数
        
        Returns:
            随机数字符串
        """
        url = f"{self.base_url}/v1/private/user/nonce/generate"
        payload = {
            "accountAddress": self.wallet_address,
            "verifyType": "LOGIN",
            "networkCode": "BSC"
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            # Four.meme API返回code为0表示成功，但是字符串格式
            if str(data.get("code")) == "0":
                nonce = data.get("data")
                logger.info(f"成功获取随机数: {nonce}")
                return nonce
            else:
                raise Exception(f"获取随机数失败: {data}")
                
        except Exception as e:
            logger.error(f"生成随机数时出错: {e}")
            raise
    
    def sign_message(self, nonce: str) -> str:
        """
        使用私钥签名消息
        
        Args:
            nonce: 随机数
            
        Returns:
            签名字符串
        """
        try:
            message = f"You are sign in Meme {nonce}"
            message_hash = encode_defunct(text=message)
            
            # 使用私钥签名
            account = Account.from_key(self.private_key)
            signature = account.sign_message(message_hash)
            
            signature_hex = signature.signature.hex()
            logger.info("消息签名成功")
            return signature_hex
            
        except Exception as e:
            logger.error(f"签名消息时出错: {e}")
            raise
    
    def login(self) -> str:
        """
        用户登录获取访问令牌
        
        Returns:
            访问令牌
        """
        try:
            # 1. 获取随机数
            nonce = self.generate_nonce()
            
            # 2. 签名消息
            signature = self.sign_message(nonce)
            
            # 3. 登录请求
            url = f"{self.base_url}/v1/private/user/login/dex"
            payload = {
                "region": "WEB",
                "langType": "EN",
                "loginIp": "",
                "inviteCode": "",
                "verifyInfo": {
                    "address": self.wallet_address,
                    "networkCode": "BSC",
                    "signature": signature,
                    "verifyType": "LOGIN"
                },
                "walletName": "MetaMask"
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if str(data.get("code")) == "0":
                self.access_token = data.get("data")
                logger.info("登录成功")
                return self.access_token
            else:
                raise Exception(f"登录失败: {data}")
                
        except Exception as e:
            logger.error(f"登录时出错: {e}")
            raise
    
    def upload_image(self, image_path: str) -> str:
        """
        上传代币图片
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            上传后的图片URL
        """
        if not self.access_token:
            raise Exception("请先登录获取访问令牌")
        
        url = f"{self.base_url}/v1/private/token/upload"
        
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                headers = {'meme-web-access': self.access_token}
                
                # 临时移除Content-Type让requests自动设置
                original_content_type = self.session.headers.get('Content-Type')
                if 'Content-Type' in self.session.headers:
                    del self.session.headers['Content-Type']
                
                response = self.session.post(url, files=files, headers=headers)
                
                # 恢复Content-Type
                if original_content_type:
                    self.session.headers['Content-Type'] = original_content_type
                
                response.raise_for_status()
                
                data = response.json()
                if str(data.get("code")) == "0":
                    image_url = data.get("data")
                    logger.info(f"图片上传成功: {image_url}")
                    return image_url
                else:
                    raise Exception(f"图片上传失败: {data}")
                    
        except FileNotFoundError:
            logger.error(f"图片文件不存在: {image_path}")
            raise
        except Exception as e:
            logger.error(f"上传图片时出错: {e}")
            raise
    
    def create_token(self, token_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建代币
        
        Args:
            token_config: 代币配置参数
            
        Returns:
            创建结果，包含签名参数
        """
        if not self.access_token:
            raise Exception("请先登录获取访问令牌")
        
        url = f"{self.base_url}/v1/private/token/create"
        
        # 设置固定参数
        payload = {
            # 可自定义参数
            "name": token_config.get("name"),
            "shortName": token_config.get("shortName"),
            "desc": token_config.get("desc"),
            "imgUrl": token_config.get("imgUrl", "https://static.four.meme/market/default-token-logo.png"),  # 使用默认图片
            "launchTime": token_config.get("launchTime", int(time.time() * 1000)),
            "label": token_config.get("label", "Meme"),
            "webUrl": token_config.get("webUrl", ""),
            "twitterUrl": token_config.get("twitterUrl", ""),
            "telegramUrl": token_config.get("telegramUrl", ""),
            "preSale": token_config.get("preSale", "0"),
            
            # 固定参数
            "totalSupply": 1000000000,
            "raisedAmount": 24,
            "saleRate": 0.8,
            "reserveRate": 0,
            "lpTradingFee": 0.0025,
            "funGroup": False,
            "clickFun": False,
            "symbol": "BNB",
            
            # raisedToken 固定配置
            "raisedToken": {
                "symbol": "BNB",
                "nativeSymbol": "BNB",
                "symbolAddress": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
                "deployCost": "0",
                "buyFee": "0.01",
                "sellFee": "0.01",
                "minTradeFee": "0",
                "b0Amount": "8",
                "totalBAmount": "24",
                "totalAmount": "1000000000",
                "logoUrl": "https://static.four.meme/market/68b871b6-96f7-408c-b8d0-388d804b34275092658264263839640.png",
                "tradeLevel": ["0.1", "0.5", "1"],
                "status": "PUBLISH",
                "buyTokenLink": "https://pancakeswap.finance/swap",
                "reservedNumber": 10,
                "saleRate": "0.8",
                "networkCode": "BSC",
                "platform": "MEME"
            }
        }
        
        try:
            headers = {'meme-web-access': self.access_token}
            response = self.session.post(url, json=payload, headers=headers)
            
            # 先记录响应状态和内容，再检查错误
            logger.info(f"API响应状态: {response.status_code}")
            try:
                response_data = response.json()
                logger.info(f"API响应内容: {response_data}")
            except:
                logger.info(f"API响应文本: {response.text}")
            
            response.raise_for_status()
            
            data = response.json()
            if str(data.get("code")) == "0":
                logger.info("代币创建请求成功")
                return {
                    "success": True,
                    **data.get("data", {})
                }
            else:
                raise Exception(f"代币创建失败: {data}")
                
        except Exception as e:
            logger.error(f"创建代币时出错: {e}")
            raise
    
    def create_token_complete(
        self, 
        token_config: Dict[str, Any], 
        image_path: Optional[str] = None, 
        deploy_on_chain: bool = True,
        purchase_amount: float = 0.0  # 新增：购买代币的BNB数量
    ) -> Dict[str, Any]:
        """
        完整的代币创建流程（API + 区块链）
        
        Args:
            token_config: 代币配置参数
            image_path: 图片路径（可选，如果token_config中已有imgUrl则不需要）
            deploy_on_chain: 是否部署到区块链
            purchase_amount: 购买代币的BNB数量（0表示仅创建不购买）
            
        Returns:
            完整的创建结果
        """
        result = {
            "success": False,
            "api_result": None,
            "blockchain_result": None,
            "error": None
        }
        
        try:
            # 1. 用户登录
            logger.info("开始用户登录...")
            login_result = self.login()
            if not login_result:
                result["error"] = "用户登录失败"
                return result
            
            # 2. 处理图片URL
            if image_path:
                # 如果提供了图片路径，上传图片
                image_url = self.upload_image(image_path)
                token_config["imgUrl"] = image_url
                logger.info(f"上传新图片: {image_url}")
            elif not token_config.get("imgUrl"):
                # 如果没有提供图片路径，也没有imgUrl，则使用默认值
                logger.warning("未提供图片，将使用默认图片URL")
                # 注意：这里不设置默认URL，让create_token方法处理
            else:
                # 使用已提供的imgUrl
                logger.info(f"使用已提供的图片URL: {token_config.get('imgUrl')}")
            
            # 3. 调用代币创建API
            logger.info("调用代币创建API...")
            api_result = self.create_token(token_config)
            result["api_result"] = api_result
            
            if not api_result or not api_result.get("success"):
                result["error"] = f"API创建失败: {api_result.get('error', '未知错误') if api_result else '无响应'}"
                return result
            
            # 4. 区块链部署（如果启用）
            if deploy_on_chain and self.blockchain_manager:
                logger.info(f"开始区块链部署，购买数量: {purchase_amount} BNB...")
                create_arg = api_result.get("createArg")
                signature = api_result.get("signature")
                
                if not create_arg or not signature:
                    result["error"] = "API返回的部署参数不完整"
                    return result
                
                blockchain_result = self.deploy_to_blockchain(create_arg, signature, purchase_amount)
                result["blockchain_result"] = blockchain_result
                
                if blockchain_result.get("success"):
                    # 合并API和区块链结果
                    result["success"] = True
                    result["token_address"] = blockchain_result.get("token_address")
                    result["tx_hash"] = blockchain_result.get("tx_hash")
                    result["purchase_amount"] = purchase_amount
                    
                    if purchase_amount > 0:
                        logger.info(f"代币创建并购买完成: {result['token_address']}, 购买了 {purchase_amount} BNB")
                    else:
                        logger.info(f"代币创建完成: {result['token_address']}")
                else:
                    result["error"] = f"区块链部署失败: {blockchain_result.get('error')}"
            else:
                # 仅API创建，不部署到区块链
                result["success"] = True
                result["create_arg"] = api_result.get("createArg")
                result["signature"] = api_result.get("signature")
                logger.info("代币API创建完成，未部署到区块链")
            
            return result
            
        except Exception as e:
            logger.error(f"完整创建流程失败: {e}")
            result["error"] = str(e)
            return result
    
    def deploy_to_blockchain(self, create_arg: str, signature: str, purchase_amount: float = 0.0) -> Dict[str, Any]:
        """
        部署代币到区块链
        
        Args:
            create_arg: API返回的创建参数
            signature: API返回的签名
            purchase_amount: 购买代币的BNB数量（0表示仅创建不购买）
            
        Returns:
            部署结果
        """
        if not self.blockchain_manager:
            return {
                "success": False,
                "error": "区块链管理器未启用"
            }
        
        logger.info(f"开始部署代币到区块链，购买数量: {purchase_amount} BNB")
        return self.blockchain_manager.create_token_on_chain(
            create_arg, 
            signature, 
            purchase_amount=purchase_amount
        )
    
    def get_wallet_balance(self) -> Optional[float]:
        """
        获取钱包BNB余额
        
        Returns:
            BNB余额，失败时返回None
        """
        if not self.blockchain_manager:
            logger.warning("区块链管理器未初始化")
            return None
        
        try:
            balance = self.blockchain_manager.get_balance()
            logger.info(f"钱包余额: {balance} BNB")
            return balance
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
            return None

    def get_token_balance(self, token_address: str) -> Optional[float]:
        """
        获取代币余额
        
        Args:
            token_address: 代币合约地址
            
        Returns:
            代币余额
        """
        if not self.blockchain_manager:
            logger.error("区块链管理器未启用，无法获取代币余额")
            return None
        
        return self.blockchain_manager.get_token_balance(token_address)
    
    def sell_token(
        self, 
        token_address: str, 
        sell_percentage: float = 100.0
    ) -> Dict[str, Any]:
        """
        卖出代币
        
        Args:
            token_address: 代币合约地址
            sell_percentage: 卖出百分比（1-100）
            
        Returns:
            卖出结果
        """
        if not self.blockchain_manager:
            return {
                "success": False,
                "error": "区块链管理器未启用"
            }
        
        logger.info(f"开始卖出代币: {token_address}, 卖出比例: {sell_percentage}%")
        return self.blockchain_manager.sell_token_complete(token_address, sell_percentage)
    



def main():
    """主函数示例"""
    # 配置信息（请替换为实际值）
    PRIVATE_KEY = "your_private_key_here"
    WALLET_ADDRESS = "your_wallet_address_here"
    
    # 代币配置
    token_config = {
        "name": "测试代币",
        "shortName": "TEST",
        "desc": "这是一个测试代币",
        "label": "Meme",
        "webUrl": "https://example.com",
        "twitterUrl": "https://x.com/example",
        "telegramUrl": "https://t.me/example",
        "preSale": "0"
    }
    
    # 图片路径（可选）
    image_path = "token_logo.png"  # 如果有图片的话
    
    try:
        # 创建机器人实例
        bot = FourMemeBot(PRIVATE_KEY, WALLET_ADDRESS)
        
        # 执行完整创建流程
        result = bot.create_token_complete(token_config, image_path if os.path.exists(image_path) else None)
        
        print("创建成功！")
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"创建失败: {e}")


if __name__ == "__main__":
    import os
    main() 