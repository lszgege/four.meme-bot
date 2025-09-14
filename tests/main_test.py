#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Four.meme 机器人真实环境测试
使用真实私钥进行完整功能测试
"""

import os
import sys
import json
import time
from typing import Dict, Any

# 添加核心模块路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_user_credentials():
    """获取用户提供的真实凭据"""
    print("🔐 请提供真实的钱包凭据进行测试")
    print("⚠️  警告: 请确保这是测试钱包，有足够的BNB支付Gas费用")
    print()
    
    private_key = input("请输入私钥 (不带0x前缀也可以): ").strip()
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    # 从私钥推导钱包地址
    try:
        from core.utils import CryptoUtils
        wallet_address = CryptoUtils.get_wallet_address_from_private_key(private_key)
        print(f"✅ 推导出钱包地址: {wallet_address}")
    except Exception as e:
        print(f"❌ 私钥格式错误: {e}")
        return None, None
    
    # 确认
    confirm = input(f"\n确认使用钱包 {wallet_address} 进行测试? (y/n): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("❌ 用户取消测试")
        return None, None
    
    return private_key, wallet_address

def test_basic_functionality(private_key: str, wallet_address: str):
    """测试基础功能"""
    print("\n🧪 第1阶段: 基础功能测试")
    print("=" * 50)
    
    try:
        from core.four_meme_bot import FourMemeBot
        
        # 创建机器人实例 (暂时不启用区块链)
        print("🤖 创建机器人实例...")
        bot = FourMemeBot(private_key, wallet_address, enable_blockchain=False)
        print("✅ 机器人创建成功")
        
        # 测试签名功能
        print("🔐 测试消息签名...")
        test_message = f"Test signature at {int(time.time())}"
        signature = bot.sign_message(test_message)
        print(f"✅ 签名成功: {signature[:20]}...")
        
        return bot
        
    except Exception as e:
        print(f"❌ 基础功能测试失败: {e}")
        return None

def test_blockchain_connection(private_key: str, wallet_address: str):
    """测试区块链连接"""
    print("\n🧪 第2阶段: 区块链连接测试")
    print("=" * 50)
    
    try:
        from core.blockchain_utils import BlockchainManager
        
        print("🌐 连接BSC网络...")
        blockchain_manager = BlockchainManager(private_key)
        print("✅ 区块链连接成功")
        
        # 检查余额
        print("💰 检查钱包余额...")
        balance = blockchain_manager.get_balance()
        print(f"✅ 当前余额: {balance:.6f} BNB")
        
        if balance < 0.001:
            print("⚠️  警告: 余额可能不足以支付Gas费用")
            print("⚠️  继续测试，但实际部署可能失败")
        
        # 获取Gas价格
        print("⛽ 获取当前Gas价格...")
        gas_price = blockchain_manager.get_gas_price()
        gas_price_gwei = blockchain_manager.web3.from_wei(gas_price, 'gwei')
        print(f"✅ 当前Gas价格: {gas_price_gwei} Gwei")
        
        return blockchain_manager
        
    except Exception as e:
        print(f"❌ 区块链连接测试失败: {e}")
        return None

def test_api_login(bot):
    """测试API登录流程"""
    print("\n🧪 第3阶段: API登录测试")
    print("=" * 50)
    
    try:
        # 生成随机数
        print("🎲 生成登录随机数...")
        nonce = bot.generate_nonce()
        print(f"✅ 随机数: {nonce}")
        
        # 执行登录
        print("🔐 执行用户登录...")
        access_token = bot.login()
        print(f"✅ 登录成功，访问令牌: {access_token[:20]}...")
        
        return access_token
        
    except Exception as e:
        print(f"❌ API登录测试失败: {e}")
        return None

def test_image_upload(bot):
    """测试图片上传"""
    print("\n🧪 第4阶段: 图片上传测试")
    print("=" * 50)
    
    # 检查图片文件
    image_files = ["logo.jpg", "logo.png", "test_logo.png", "token_logo.png"]
    image_path = None
    
    for img_file in image_files:
        if os.path.exists(img_file):
            image_path = img_file
            break
    
    if not image_path:
        print("⚠️  没有找到图片文件，创建一个测试图片...")
        try:
            from PIL import Image
            # 创建一个简单的测试图片
            img = Image.new('RGB', (200, 200), color='blue')
            image_path = "test_logo.png"
            img.save(image_path)
            print(f"✅ 创建测试图片: {image_path}")
        except Exception as e:
            print(f"❌ 无法创建测试图片: {e}")
            return None
    
    try:
        print(f"🖼️  准备上传图片: {image_path}")
        
        # 上传图片
        print("🚀 开始上传图片...")
        image_url = bot.upload_image(image_path)
        print(f"✅ 图片上传成功: {image_url}")
        
        return image_url
        
    except Exception as e:
        print(f"❌ 图片上传失败: {e}")
        return None

def test_token_creation_api(bot, image_url=None):
    """测试代币创建API"""
    print("\n🧪 第5阶段: 代币创建API测试")
    print("=" * 50)
    
    try:
        # 准备测试代币配置
        token_config = {
            "name": f"测试代币{int(time.time())}",
            "shortName": f"TEST{str(int(time.time()))[-4:]}",
            "desc": "这是一个真实环境测试代币，用于验证API功能",
            "label": "AI",  # 必需的标签字段
            "webUrl": "https://test-token-example.com",  # 使用正确的字段名
            "twitterUrl": "",  # 社交信息为空
            "telegramUrl": "",  # 社交信息为空
            "preSale": "0"  # 预售金额
        }
        
        # 如果有上传的图片URL，使用它
        if image_url:
            token_config["imgUrl"] = image_url
            print(f"🖼️  使用上传的图片: {image_url}")
        
        print("📝 代币配置:")
        for key, value in token_config.items():
            print(f"   {key}: {value}")
        
        # 调用创建API
        print("🚀 调用代币创建API...")
        api_result = bot.create_token(token_config)
        print("✅ API调用成功")
        
        # 显示返回结果
        print("📋 API返回结果:")
        if "createArg" in api_result:
            print(f"   创建参数: {api_result['createArg'][:30]}...")
        if "signature" in api_result:
            print(f"   平台签名: {api_result['signature'][:30]}...")
        
        return api_result
        
    except Exception as e:
        print(f"❌ 代币创建API测试失败: {e}")
        return None

def test_full_deployment(private_key: str, wallet_address: str, image_url: str = None):
    """测试完整部署流程"""
    print("\n🧪 第6阶段: 完整部署测试")
    print("=" * 50)
    
    # 询问用户是否继续
    print("⚠️  注意: 这将在BSC主网上创建真实的代币合约")
    print("💰 这将消耗真实的BNB作为Gas费用")
    confirm = input("确认继续完整部署测试? (y/n): ").lower().strip()
    
    if confirm not in ['y', 'yes']:
        print("❌ 用户取消完整部署测试")
        return None
    
    try:
        from core.four_meme_bot import FourMemeBot
        
        # 创建启用区块链的机器人
        print("🤖 创建完整功能机器人...")
        bot = FourMemeBot(private_key, wallet_address, enable_blockchain=True)
        
        # 检查余额
        balance = bot.get_wallet_balance()
        if balance and balance < 0.01:
            print(f"❌ 余额不足: {balance} BNB < 0.01 BNB")
            return None
        
        # 准备代币配置
        token_config = {
            "name": f"真实测试币{int(time.time())}",
            "shortName": f"REAL{str(int(time.time()))[-4:]}",
            "desc": "这是一个真实部署的测试代币",
            "label": "AI",  # 必需的标签字段
            "webUrl": "https://real-test-token-example.com",  # 使用正确的字段名
            "twitterUrl": "",  # 社交信息为空
            "telegramUrl": "",  # 社交信息为空
            "preSale": "0"  # 预售金额
        }
        
        # 如果有之前上传的图片URL，使用它
        if image_url:
            token_config["imgUrl"] = image_url
            print(f"🖼️  使用之前上传的图片: {image_url}")
        
        print("📝 最终代币配置:")
        for key, value in token_config.items():
            print(f"   {key}: {value}")
        
        # 执行完整创建流程
        print("🚀 执行完整创建和部署流程...")
        print("   这包括: API调用 → 获取签名 → 区块链部署 → 交易确认")
        
        result = bot.create_token_complete(
            token_config, 
            image_path=None,  # 不重新上传图片
            deploy_on_chain=True
        )
        
        # 显示结果
        print("\n🎉 完整部署流程完成!")
        print("📊 最终结果:")
        
        if result.get("success"):
            print("✅ 部署成功!")
            if result.get("token_address"):
                token_addr = result["token_address"]
                print(f"🏠 代币合约地址: {token_addr}")
                print(f"🔗 BSCScan查看: https://bscscan.com/token/{token_addr}")
            
            if result.get("tx_hash"):
                tx_hash = result["tx_hash"]
                print(f"📋 部署交易哈希: {tx_hash}")
                print(f"🔗 BSCScan查看: https://bscscan.com/tx/{tx_hash}")
        else:
            print(f"❌ 部署失败: {result.get('error', '未知错误')}")
        
        return result
        
    except Exception as e:
        print(f"❌ 完整部署测试失败: {e}")
        return None

def test_token_purchase(bot, token_address: str):
    """测试代币购买"""
    print("\n🧪 第7阶段: 代币购买测试")
    print("=" * 50)
    
    try:
        # 检查钱包余额
        print("💰 检查钱包余额...")
        balance = bot.get_wallet_balance()
        print(f"✅ 当前余额: {balance:.6f} BNB")
        
        if balance < 0.01:
            print("❌ 余额不足，跳过购买测试")
            return None
        
        # 询问购买金额
        purchase_amount = input("请输入购买金额 (BNB, 建议0.001-0.01): ").strip()
        try:
            purchase_amount = float(purchase_amount)
            if purchase_amount <= 0 or purchase_amount > balance * 0.5:
                print("❌ 购买金额无效")
                return None
        except ValueError:
            print("❌ 购买金额格式错误")
            return None
        
        print(f"🛒 购买 {purchase_amount} BNB 的代币...")
        # 直接调用区块链管理器的购买方法
        result = bot.blockchain_manager._buy_token(token_address, purchase_amount)
        
        if result and result.get("success"):
            print("✅ 代币购买成功!")
            if result.get("tx_hash"):
                print(f"📋 购买交易哈希: {result['tx_hash']}")
            
            # 检查代币余额
            print("🔍 检查代币余额...")
            token_balance = bot.get_token_balance(token_address)
            if token_balance:
                print(f"✅ 代币余额: {token_balance}")
            
            return result
        else:
            print(f"❌ 代币购买失败: {result.get('error') if result else '未知错误'}")
            return None
            
    except Exception as e:
        print(f"❌ 代币购买测试失败: {e}")
        return None

def test_token_sell(bot, token_address: str):
    """测试代币卖出"""
    print("\n🧪 第8阶段: 代币卖出测试")
    print("=" * 50)
    
    try:
        # 检查代币余额
        print("🔍 检查代币余额...")
        token_balance = bot.get_token_balance(token_address)
        if not token_balance or token_balance <= 0:
            print("❌ 没有代币余额，跳过卖出测试")
            return None
        
        print(f"✅ 代币余额: {token_balance}")
        
        # 询问卖出百分比
        sell_percentage = input("请输入卖出百分比 (例如: 50 表示50%): ").strip()
        try:
            sell_percentage = float(sell_percentage)
            if sell_percentage <= 0 or sell_percentage > 100:
                print("❌ 卖出百分比无效")
                return None
        except ValueError:
            print("❌ 卖出百分比格式错误")
            return None
        
        print(f"💰 卖出 {sell_percentage}% 的代币...")
        result = bot.sell_token(token_address, sell_percentage)
        
        if result and result.get("success"):
            print("✅ 代币卖出成功!")
            if result.get("tx_hash"):
                print(f"📋 卖出交易哈希: {result['tx_hash']}")
            if result.get("bnb_received"):
                print(f"💰 获得 BNB: {result['bnb_received']}")
            
            return result
        else:
            print(f"❌ 代币卖出失败: {result.get('error') if result else '未知错误'}")
            return None
            
    except Exception as e:
        print(f"❌ 代币卖出测试失败: {e}")
        return None

def main():
    """主测试函数"""
    print("🚀 Four.meme 机器人真实环境全面测试")
    print("=" * 60)
    print("⚠️  警告: 这将使用真实私钥和BNB进行测试")
    print("💡 建议: 使用测试钱包，确保有足够的BNB余额")
    print()
    
    # 获取用户凭据
    private_key, wallet_address = get_user_credentials()
    if not private_key or not wallet_address:
        return
    
    # 设置环境变量
    os.environ['FOUR_PRIVATE_KEY'] = private_key
    os.environ['FOUR_WALLET_ADDRESS'] = wallet_address
    
    print(f"\n📍 测试钱包: {wallet_address}")
    print("🌐 目标网络: BSC主网")
    print()
    
    # 阶段性测试
    test_results = {}
    
    # 第1阶段: 基础功能
    bot = test_basic_functionality(private_key, wallet_address)
    test_results["基础功能"] = bot is not None
    
    if not bot:
        print("❌ 基础功能测试失败，停止后续测试")
        return
    
    # 第2阶段: 区块链连接
    blockchain_manager = test_blockchain_connection(private_key, wallet_address)
    test_results["区块链连接"] = blockchain_manager is not None
    
    # 第3阶段: API登录
    access_token = test_api_login(bot)
    test_results["API登录"] = access_token is not None
    
    if not access_token:
        print("❌ API登录失败，跳过后续API测试")
        image_url = None
        api_result = None
    else:
        # 第4阶段: 图片上传
        image_url = test_image_upload(bot)
        test_results["图片上传"] = image_url is not None
        
        # 第5阶段: 代币创建API
        api_result = test_token_creation_api(bot, image_url)
        test_results["代币创建API"] = api_result is not None
    
    # 第6阶段: 完整部署 (可选)
    deployment_result = None
    token_address = None
    if blockchain_manager and access_token and api_result:
        deployment_result = test_full_deployment(private_key, wallet_address, image_url)
        test_results["完整部署"] = deployment_result is not None and deployment_result.get("success", False)
        
        if deployment_result and deployment_result.get("success"):
            token_address = deployment_result.get("token_address")
    
    # 第7阶段: 代币购买测试 (可选)
    purchase_result = None
    if token_address and deployment_result and deployment_result.get("success"):
        try:
            from core.four_meme_bot import FourMemeBot
            full_bot = FourMemeBot(private_key, wallet_address, enable_blockchain=True)
            purchase_result = test_token_purchase(full_bot, token_address)
            test_results["代币购买"] = purchase_result is not None and purchase_result.get("success", False)
        except Exception as e:
            print(f"❌ 代币购买测试初始化失败: {e}")
            test_results["代币购买"] = False
    
    # 第8阶段: 代币卖出测试 (可选)
    if token_address and purchase_result and purchase_result.get("success"):
        try:
            from core.four_meme_bot import FourMemeBot
            full_bot = FourMemeBot(private_key, wallet_address, enable_blockchain=True)
            sell_result = test_token_sell(full_bot, token_address)
            test_results["代币卖出"] = sell_result is not None and sell_result.get("success", False)
        except Exception as e:
            print(f"❌ 代币卖出测试初始化失败: {e}")
            test_results["代币卖出"] = False
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！机器人功能完全正常")
    else:
        print(f"⚠️  有 {total - passed} 项测试失败，请检查相关功能")
    
    print("\n💡 提示: 查看日志文件获取详细信息")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程出现异常: {e}")
        import traceback
        traceback.print_exc() 