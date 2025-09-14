#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Four.meme 代币创建机器人使用示例
"""

import os
import sys
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入机器人模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.four_meme_bot import FourMemeBot
from core.config import Config
from core.utils import TokenUtils, ImageUtils

def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 验证配置
    if not Config.validate_config():
        print("❌ 配置验证失败，请检查环境变量设置")
        return False
    
    try:
        # 创建机器人实例
        bot = FourMemeBot(Config.PRIVATE_KEY, Config.WALLET_ADDRESS)
        
        # 代币配置
        token_config = {
            "name": "示例代币",
            "shortName": "DEMO",
            "desc": "这是一个使用机器人创建的示例代币，仅用于测试目的",
            "label": "Meme",
            "webUrl": "https://example.com",
            "twitterUrl": "https://x.com/example",
            "telegramUrl": "https://t.me/example",
            "preSale": "0"
        }
        
        print(f"📝 代币配置: {token_config}")
        
        # 执行完整创建流程
        print("🚀 开始创建代币...")
        result = bot.create_token_complete(token_config)
        
        print("✅ 代币创建成功！")
        print(f"📋 结果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def example_with_image():
    """包含图片上传的示例"""
    print("\n=== 图片上传示例 ===")
    
    # 检查是否有示例图片
    image_path = "example_logo.png"
    if not os.path.exists(image_path):
        print(f"⚠️  示例图片不存在: {image_path}")
        print("请准备一个PNG图片文件作为代币Logo")
        return False
    
    # 验证图片
    if not ImageUtils.validate_image(image_path):
        print("❌ 图片验证失败")
        return False
    
    try:
        # 创建机器人实例
        bot = FourMemeBot(Config.PRIVATE_KEY, Config.WALLET_ADDRESS)
        
        # 代币配置
        token_config = {
            "name": "带Logo的代币",
            "shortName": "LOGO",
            "desc": "这是一个带有自定义Logo的示例代币",
            "label": "AI",
            "webUrl": "https://mytoken.com",
            "twitterUrl": "https://x.com/mytoken",
            "telegramUrl": "https://t.me/mytoken",
            "preSale": "0.1"  # 预售0.1 BNB
        }
        
        print(f"📝 代币配置: {token_config}")
        print(f"🖼️  图片路径: {image_path}")
        
        # 执行完整创建流程（包含图片上传）
        print("🚀 开始创建代币（包含图片上传）...")
        result = bot.create_token_complete(token_config, image_path)
        
        print("✅ 代币创建成功（含Logo）！")
        print(f"📋 结果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def example_step_by_step():
    """分步执行示例"""
    print("\n=== 分步执行示例 ===")
    
    try:
        # 创建机器人实例
        bot = FourMemeBot(Config.PRIVATE_KEY, Config.WALLET_ADDRESS)
        
        # 步骤1: 登录
        print("🔐 步骤1: 用户登录...")
        access_token = bot.login()
        print(f"✅ 登录成功，访问令牌: {access_token[:20]}...")
        
        # 步骤2: 代币配置验证
        print("📋 步骤2: 验证代币配置...")
        token_config = {
            "name": "分步创建代币",
            "shortName": "STEP",
            "desc": "这是一个分步创建的示例代币",
            "label": "DeFi"
        }
        
        # 验证配置
        errors = TokenUtils.validate_token_config(token_config)
        if errors:
            print(f"❌ 配置验证失败: {errors}")
            return False
        print("✅ 配置验证通过")
        
        # 步骤3: 创建代币
        print("🚀 步骤3: 创建代币...")
        result = bot.create_token(token_config)
        
        print("✅ 分步创建完成！")
        print(f"📋 结果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分步创建失败: {e}")
        return False

def example_batch_creation():
    """批量创建示例"""
    print("\n=== 批量创建示例 ===")
    
    # 多个代币配置
    token_configs = [
        {
            "name": "批量代币1",
            "shortName": "BATCH1",
            "desc": "第一个批量创建的代币",
            "label": "Meme"
        },
        {
            "name": "批量代币2", 
            "shortName": "BATCH2",
            "desc": "第二个批量创建的代币",
            "label": "Games"
        },
        {
            "name": "批量代币3",
            "shortName": "BATCH3", 
            "desc": "第三个批量创建的代币",
            "label": "Social"
        }
    ]
    
    try:
        # 创建机器人实例
        bot = FourMemeBot(Config.PRIVATE_KEY, Config.WALLET_ADDRESS)
        
        # 先登录一次
        bot.login()
        
        results = []
        for i, config in enumerate(token_configs, 1):
            print(f"🚀 创建第 {i} 个代币: {config['name']}")
            
            try:
                result = bot.create_token(config)
                results.append({"config": config, "result": result, "success": True})
                print(f"✅ 第 {i} 个代币创建成功")
                
                # 避免请求过于频繁
                if i < len(token_configs):
                    print("⏳ 等待2秒...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ 第 {i} 个代币创建失败: {e}")
                results.append({"config": config, "error": str(e), "success": False})
        
        # 输出批量创建结果
        print(f"\n📊 批量创建完成，成功: {sum(1 for r in results if r['success'])} / {len(results)}")
        
        for i, result in enumerate(results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{status} 代币 {i}: {result['config']['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 批量创建失败: {e}")
        return False

def main():
    """主函数"""
    print("🤖 Four.meme 代币创建机器人示例")
    print("=" * 50)
    
    # 检查配置
    if not Config.validate_config():
        print("❌ 请先配置环境变量 FOUR_PRIVATE_KEY 和 FOUR_WALLET_ADDRESS")
        print("💡 提示: 运行 'python config.py' 生成配置模板")
        return
    
    print(f"✅ 配置验证通过")
    print(f"📍 钱包地址: {Config.WALLET_ADDRESS}")
    print(f"🌐 网络: {Config.NETWORK_CODE}")
    
    # 运行示例
    examples = [
        ("基本使用", example_basic_usage),
        ("图片上传", example_with_image), 
        ("分步执行", example_step_by_step),
        ("批量创建", example_batch_creation)
    ]
    
    for name, func in examples:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            success = func()
            if success:
                print(f"✅ {name} 示例执行成功")
            else:
                print(f"❌ {name} 示例执行失败")
        except KeyboardInterrupt:
            print(f"\n⏹️  用户中断了 {name} 示例")
            break
        except Exception as e:
            print(f"❌ {name} 示例出现异常: {e}")
        
        # 询问是否继续
        if name != examples[-1][0]:  # 不是最后一个示例
            try:
                choice = input("\n继续下一个示例？(y/n): ").lower().strip()
                if choice not in ['y', 'yes', '']:
                    break
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
    
    print(f"\n🎉 所有示例执行完成！")
    print(f"📝 查看日志文件: {Config.LOG_FILE}")

if __name__ == "__main__":
    main() 