#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Four.meme Bot - 主入口文件
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import FourMemeBot, Config

def main():
    """主函数 - 提供简单的命令行界面"""
    print("🚀 Four.meme 代币创建机器人")
    print("=" * 50)
    
    # 验证配置
    if not Config.validate_config():
        print("❌ 配置验证失败，请检查环境变量设置")
        return
    
    print("✅ 配置验证通过")
    print("\n选择操作模式:")
    print("1. 运行完整测试")
    print("2. 查看使用示例")
    print("3. 退出")
    
    try:
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            print("\n🧪 启动完整测试...")
            # 导入并运行测试
            from tests.main_test import main as run_tests
            run_tests()
        elif choice == "2":
            print("\n📖 查看示例...")
            print("请运行以下命令查看使用示例:")
            print("  python examples/example.py")
            print("  python examples/complete_example.py")
        elif choice == "3":
            print("\n👋 再见！")
        else:
            print("\n❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，再见！")
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")

if __name__ == "__main__":
    main() 