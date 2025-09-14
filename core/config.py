#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Four.meme 机器人配置文件
"""

import os
from typing import Dict, Any


class Config:
    """配置管理类"""
    
    # API 配置
    BASE_URL = "https://four.meme/meme-api"
    
    # 网络配置
    NETWORK_CODE = "BSC"
    
    # 钱包配置（从环境变量读取，确保安全性）
    PRIVATE_KEY = os.getenv("FOUR_PRIVATE_KEY", "")
    WALLET_ADDRESS = os.getenv("FOUR_WALLET_ADDRESS", "")
    
    # 请求配置
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # 秒
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "four_meme_bot.log"
    
    # 代币创建固定参数
    FIXED_TOKEN_PARAMS = {
        "totalSupply": 1000000000,
        "raisedAmount": 24,
        "saleRate": 0.8,
        "reserveRate": 0,
        "lpTradingFee": 0.0025,
        "funGroup": False,
        "clickFun": False,
        "symbol": "BNB"
    }
    
    # raisedToken 固定配置
    RAISED_TOKEN_CONFIG = {
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
    
    # 支持的代币分类
    SUPPORTED_LABELS = [
        "Meme", "AI", "Defi", "Games", "Infra", 
        "De-Sci", "Social", "Depin", "Charity", "Others"
    ]
    
    # 支持的图片格式
    SUPPORTED_IMAGE_FORMATS = [".jpeg", ".jpg", ".png", ".gif", ".bmp", ".webp"]
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        验证配置是否完整
        
        Returns:
            配置是否有效
        """
        if not cls.PRIVATE_KEY:
            print("错误: 未设置私钥环境变量 FOUR_PRIVATE_KEY")
            return False
            
        if not cls.WALLET_ADDRESS:
            print("错误: 未设置钱包地址环境变量 FOUR_WALLET_ADDRESS")
            return False
            
        if not cls.PRIVATE_KEY.startswith("0x"):
            cls.PRIVATE_KEY = "0x" + cls.PRIVATE_KEY
            
        return True
    
    @classmethod
    def get_token_template(cls) -> Dict[str, Any]:
        """
        获取代币配置模板
        
        Returns:
            代币配置模板
        """
        return {
            "name": "",           # 代币名称（必填）
            "shortName": "",      # 代币符号（必填）
            "desc": "",           # 代币描述（必填）
            "imgUrl": "",         # 图片URL（上传后自动设置）
            "label": "Meme",      # 代币分类
            "webUrl": "",         # 项目网站
            "twitterUrl": "",     # 推特链接
            "telegramUrl": "",    # 电报群链接
            "preSale": "0",       # 预售金额
            "launchTime": None    # 启动时间（自动设置为当前时间）
        }


# 示例配置文件 .env
ENV_TEMPLATE = """
# Four.meme 机器人环境变量配置
# 请复制此文件为 .env 并填入实际值

# 钱包配置
FOUR_PRIVATE_KEY=your_private_key_here
FOUR_WALLET_ADDRESS=your_wallet_address_here

# 可选配置
# FOUR_LOG_LEVEL=INFO
# FOUR_REQUEST_TIMEOUT=30
"""

if __name__ == "__main__":
    # 生成 .env 模板文件
    with open(".env.template", "w", encoding="utf-8") as f:
        f.write(ENV_TEMPLATE)
    
    print("已生成 .env.template 文件")
    print("请复制为 .env 文件并填入实际配置")
    
    # 验证当前配置
    if Config.validate_config():
        print("配置验证通过")
    else:
        print("配置验证失败，请检查环境变量设置") 