#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Four.meme 完整调用逻辑示例
展示从API调用到区块链部署的完整流程
"""

import os
import json
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.four_meme_bot import FourMemeBot
from core.config import Config

def demonstrate_complete_flow():
    """演示完整的代币创建流程"""
    print("🚀 Four.meme 完整代币创建流程演示")
    print("=" * 60)
    
    # 1. 配置验证
    print("📋 第1步: 验证配置...")
    if not Config.validate_config():
        print("❌ 配置验证失败，请设置环境变量")
        return
    print("✅ 配置验证通过")
    
    # 2. 创建机器人实例
    print("\n🤖 第2步: 初始化机器人...")
    try:
        # enable_blockchain=True 启用区块链交互
        bot = FourMemeBot(
            Config.PRIVATE_KEY, 
            Config.WALLET_ADDRESS, 
            enable_blockchain=True
        )
        print("✅ 机器人初始化成功")
        
        # 检查钱包余额
        balance = bot.get_wallet_balance()
        if balance is not None:
            print(f"💰 钱包余额: {balance:.4f} BNB")
            if balance < 0.01:  # 假设需要至少0.01 BNB的Gas费
                print("⚠️  警告: 钱包余额可能不足以支付Gas费用")
        
    except Exception as e:
        print(f"❌ 机器人初始化失败: {e}")
        return
    
    # 3. 准备代币配置
    print("\n📝 第3步: 准备代币配置...")
    token_config = {
        "name": "演示代币",
        "shortName": "DEMO",
        "desc": "这是一个完整流程演示代币，包含API调用和区块链部署",
        "label": "Meme",
        "webUrl": "https://demo-token.example.com",
        "twitterUrl": "https://x.com/demo_token",
        "telegramUrl": "https://t.me/demo_token",
        "preSale": "0"
    }
    
    print("📋 代币配置:")
    for key, value in token_config.items():
        print(f"   {key}: {value}")
    
    # 4. 执行完整创建流程
    print("\n🔄 第4步: 执行完整创建流程...")
    print("   这包括以下子步骤:")
    print("   4.1 用户登录认证")
    print("   4.2 调用代币创建API")
    print("   4.3 获取签名参数")
    print("   4.4 部署到区块链")
    print("   4.5 等待交易确认")
    print("   4.6 解析代币地址")
    
    try:
        # deploy_on_chain=True 表示要部署到区块链
        result = bot.create_token_complete(
            token_config, 
            image_path=None,  # 暂时不上传图片
            deploy_on_chain=True
        )
        
        print("\n🎉 创建流程完成！")
        print("📊 结果详情:")
        
        # 显示API结果
        if "api_result" in result:
            print("   📡 API调用结果: 成功")
            api_data = result["api_result"]
            if "createArg" in api_data:
                print(f"   📝 创建参数: {api_data['createArg'][:20]}...")
            if "signature" in api_data:
                print(f"   ✍️  平台签名: {api_data['signature'][:20]}...")
        
        # 显示区块链结果
        if "blockchain_result" in result:
            blockchain_data = result["blockchain_result"]
            if blockchain_data.get("success"):
                print("   ⛓️  区块链部署: 成功")
                print(f"   🏠 代币地址: {blockchain_data.get('token_address')}")
                print(f"   📋 交易哈希: {blockchain_data.get('tx_hash')}")
                print(f"   🏗️  区块高度: {blockchain_data.get('block_number')}")
                print(f"   ⛽ Gas使用: {blockchain_data.get('gas_used')}")
            else:
                print("   ❌ 区块链部署失败")
                print(f"   🔍 错误信息: {blockchain_data.get('error')}")
        
        # 总体成功状态
        if result.get("success"):
            print("\n✅ 代币创建完全成功！")
            if result.get("token_address"):
                token_addr = result["token_address"]
                print(f"🎊 您的代币已部署到: {token_addr}")
                print(f"🔗 BSCScan查看: https://bscscan.com/token/{token_addr}")
        else:
            print(f"\n❌ 代币创建失败: {result.get('error', '未知错误')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 创建流程异常: {e}")
        return None

def demonstrate_step_by_step():
    """演示分步执行流程"""
    print("\n" + "=" * 60)
    print("🔍 分步执行演示（仅API调用，不部署区块链）")
    print("=" * 60)
    
    try:
        # 创建机器人实例，但不启用区块链
        bot = FourMemeBot(
            Config.PRIVATE_KEY, 
            Config.WALLET_ADDRESS, 
            enable_blockchain=False  # 仅API模式
        )
        
        # 步骤1: 登录
        print("🔐 步骤1: 用户登录...")
        access_token = bot.login()
        print(f"✅ 登录成功: {access_token[:20]}...")
        
        # 步骤2: 创建代币（仅API）
        print("\n📝 步骤2: 调用创建API...")
        token_config = {
            "name": "API测试代币",
            "shortName": "APITEST",
            "desc": "仅用于测试API调用的代币",
            "label": "AI"
        }
        
        api_result = bot.create_token(token_config)
        print("✅ API调用成功")
        print(f"📋 返回数据: {json.dumps(api_result, indent=2, ensure_ascii=False)}")
        
        # 步骤3: 如果有区块链管理器，可以手动部署
        if bot.blockchain_manager:
            print("\n⛓️  步骤3: 手动部署到区块链...")
            create_arg = api_result.get("createArg")
            signature = api_result.get("signature")
            
            if create_arg and signature:
                blockchain_result = bot.deploy_to_blockchain(create_arg, signature)
                print(f"✅ 区块链部署结果: {blockchain_result}")
            else:
                print("❌ 缺少签名参数，无法部署")
        
        return api_result
        
    except Exception as e:
        print(f"❌ 分步执行失败: {e}")
        return None

def main():
    """主函数"""
    print("🌟 Four.meme 代币创建机器人 - 完整调用逻辑演示")
    print("这个演示将展示从API调用到区块链部署的完整过程")
    print()
    
    # 检查配置
    if not Config.validate_config():
        print("❌ 请先配置环境变量 FOUR_PRIVATE_KEY 和 FOUR_WALLET_ADDRESS")
        return
    
    print(f"📍 使用钱包: {Config.WALLET_ADDRESS}")
    print(f"🌐 目标网络: {Config.NETWORK_CODE}")
    print()
    
    # 询问用户选择
    print("请选择演示模式:")
    print("1. 完整流程（API + 区块链部署）")
    print("2. 分步执行（仅API调用）")
    print("3. 两者都执行")
    
    try:
        choice = input("\n请输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            demonstrate_complete_flow()
        elif choice == "2":
            demonstrate_step_by_step()
        elif choice == "3":
            demonstrate_complete_flow()
            demonstrate_step_by_step()
        else:
            print("无效选择，执行完整流程...")
            demonstrate_complete_flow()
    
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出演示")
    except Exception as e:
        print(f"\n❌ 演示过程出错: {e}")
    
    print("\n📝 演示完成！查看日志文件获取详细信息")

if __name__ == "__main__":
    main() 