#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Four.meme 批量执行脚本
支持从txt文件读取多个钱包信息，批量创建、购买和卖出代币
"""

import os
import sys
import time
import csv
import random
from pathlib import Path
from typing import List, Dict, Any
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import FourMemeBot, Config
from core.utils import CryptoUtils

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/batch_runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchRunner:
    """批量执行器"""
    
    def __init__(self, images_folder: str = None):
        self.results = []
        self.success_count = 0
        self.failed_count = 0
        self.images_folder = images_folder
        self.available_images = []
        self.used_images = set()  # 跟踪已使用的图片，避免重复
        
        # 加载图片文件列表
        if images_folder and os.path.exists(images_folder):
            self._load_images()
    
    def _load_images(self):
        """加载图片文件夹中的所有图片"""
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        try:
            for file_path in Path(self.images_folder).iterdir():
                if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                    self.available_images.append(str(file_path))
            
            logger.info(f"从文件夹 {self.images_folder} 加载了 {len(self.available_images)} 张图片")
            
            if not self.available_images:
                logger.warning(f"图片文件夹中没有找到支持的图片格式: {supported_formats}")
                
        except Exception as e:
            logger.error(f"加载图片文件夹失败: {e}")
    
    def _get_random_image(self) -> str:
        """随机选择一张未使用的图片"""
        if not self.available_images:
            return None
        
        # 如果所有图片都用过了，重置已使用列表
        if len(self.used_images) >= len(self.available_images):
            self.used_images.clear()
            logger.info("所有图片都已使用过，重置图片使用记录")
        
        # 选择未使用的图片
        available_unused = [img for img in self.available_images if img not in self.used_images]
        if not available_unused:
            available_unused = self.available_images
        
        selected_image = random.choice(available_unused)
        self.used_images.add(selected_image)
        
        logger.info(f"选择图片: {os.path.basename(selected_image)}")
        return selected_image
    
    def load_wallets_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        从txt文件加载钱包信息
        
        文件格式：地址;私钥;购买金额;卖出百分比
        """
        wallets = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        parts = line.split(';')
                        if len(parts) < 2:
                            logger.warning(f"第{line_num}行格式错误，跳过: {line}")
                            continue
                        
                        wallet_address = parts[0].strip()
                        private_key = parts[1].strip()
                        
                        # 添加0x前缀（如果没有）
                        if not private_key.startswith('0x'):
                            private_key = '0x' + private_key
                        
                        # 验证私钥格式
                        try:
                            derived_address = CryptoUtils.get_wallet_address_from_private_key(private_key)
                            if derived_address.lower() != wallet_address.lower():
                                logger.warning(f"第{line_num}行地址与私钥不匹配: {wallet_address} != {derived_address}")
                        except Exception as e:
                            logger.error(f"第{line_num}行私钥格式错误: {e}")
                            continue
                        
                        # 解析购买金额
                        purchase_amount = 0.0
                        if len(parts) > 2 and parts[2].strip():
                            try:
                                purchase_amount = float(parts[2].strip())
                            except ValueError:
                                logger.warning(f"第{line_num}行购买金额格式错误，使用默认值0: {parts[2]}")
                        
                        # 解析卖出百分比
                        sell_percentage = 100.0
                        if len(parts) > 3 and parts[3].strip():
                            try:
                                sell_percentage = float(parts[3].strip())
                                if sell_percentage < 0 or sell_percentage > 100:
                                    logger.warning(f"第{line_num}行卖出百分比超出范围，使用默认值100: {parts[3]}")
                                    sell_percentage = 100.0
                            except ValueError:
                                logger.warning(f"第{line_num}行卖出百分比格式错误，使用默认值100: {parts[3]}")
                        
                        wallet_info = {
                            'address': wallet_address,
                            'private_key': private_key,
                            'purchase_amount': purchase_amount,
                            'sell_percentage': sell_percentage,
                            'line_num': line_num
                        }
                        
                        wallets.append(wallet_info)
                        logger.info(f"加载钱包 {line_num}: {wallet_address[:10]}...{wallet_address[-6:]} (购买:{purchase_amount} BNB, 卖出:{sell_percentage}%)")
                        
                    except Exception as e:
                        logger.error(f"解析第{line_num}行时出错: {e}")
                        continue
                        
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            return []
        except Exception as e:
            logger.error(f"读取文件时出错: {e}")
            return []
        
        logger.info(f"成功加载 {len(wallets)} 个钱包")
        return wallets
    
    def create_token_config(self, wallet_num: int) -> Dict[str, Any]:
        """创建真实的代币配置"""
        # 真实的代币名称池
        token_names = [
            "Moon", "Rocket", "Diamond", "Golden", "Cyber", "Quantum", "Stellar", "Phoenix",
            "Thunder", "Lightning", "Fire", "Ice", "Storm", "Wind", "Earth", "Ocean",
            "Alpha", "Beta", "Gamma", "Delta", "Omega", "Prime", "Ultra", "Super",
            "Mega", "Giga", "Tera", "Nova", "Apex", "Elite", "Pro", "Max",
            "King", "Queen", "Lord", "Master", "Champion", "Legend", "Hero", "Warrior",
            "Dragon", "Tiger", "Lion", "Eagle", "Wolf", "Bear", "Shark", "Falcon",
            "Crypto", "Block", "Chain", "Hash", "Node", "Mint", "Stake", "Yield",
            "DeFi", "NFT", "Meta", "Web3", "DAO", "DEX", "AMM", "LP"
        ]
        
        # 代币后缀
        suffixes = [
            "Token", "Coin", "Finance", "Protocol", "Network", "Chain", "Swap",
            "DAO", "AI", "Bot", "Lab", "Tech", "Verse", "World", "Land"
        ]
        
        # 随机生成代币名称
        base_name = random.choice(token_names)
        suffix = random.choice(suffixes)
        full_name = f"{base_name} {suffix}"
        
        # 生成代币符号（2-5个字符）
        if len(base_name) <= 4:
            symbol = base_name.upper()
        else:
            symbol = base_name[:3].upper() + base_name[-1].upper()
        
        # 添加随机数字避免重复
        symbol += str(random.randint(10, 99))
        
        # 真实的描述模板
        descriptions = [
            f"{full_name} is a revolutionary cryptocurrency designed for the future of decentralized finance.",
            f"Join the {base_name} revolution! {full_name} brings innovation to the blockchain ecosystem.",
            f"{full_name} - Empowering the next generation of digital assets and smart contracts.",
            f"Experience the power of {base_name}! {full_name} is building the future of Web3.",
            f"{full_name} combines cutting-edge technology with community-driven governance.",
            f"Welcome to {base_name}! {full_name} is your gateway to decentralized opportunities.",
            f"{full_name} - Where innovation meets opportunity in the world of cryptocurrency.",
            f"Discover {base_name}! {full_name} is revolutionizing how we think about digital value."
        ]
        
        # 随机选择标签
        labels = ["AI", "Meme", "DeFi", "Games", "Social", "Others"]
        
        # 真实的网站域名
        domains = [
            "finance", "protocol", "network", "chain", "swap", "defi", "crypto",
            "token", "coin", "dao", "tech", "lab", "verse", "world", "app"
        ]
        
        website_name = base_name.lower() + random.choice(domains)
        
        return {
            "name": full_name,
            "shortName": symbol,
            "desc": random.choice(descriptions),
            "label": random.choice(labels),
            "webUrl": f"https://{website_name}.com",
            "twitterUrl": "",
            "telegramUrl": "",
            "preSale": "0"
        }
    
    def process_wallet(self, wallet_info: Dict[str, Any], wallet_num: int, total_wallets: int) -> Dict[str, Any]:
        """处理单个钱包"""
        logger.info(f"🔄 处理钱包 {wallet_num}/{total_wallets}: {wallet_info['address'][:10]}...{wallet_info['address'][-6:]}")
        
        result = {
            'wallet_num': wallet_num,
            'address': wallet_info['address'],
            'success': False,
            'token_address': None,
            'token_name': None,
            'token_symbol': None,
            'image_used': None,
            'create_tx': None,
            'buy_tx': None,
            'sell_tx': None,
            'error': None,
            'steps_completed': []
        }
        
        try:
            # 创建机器人实例
            bot = FourMemeBot(
                wallet_info['private_key'], 
                wallet_info['address'], 
                enable_blockchain=True
            )
            
            # 检查钱包余额
            balance = bot.get_wallet_balance()
            if balance < 0.01:
                raise Exception(f"钱包余额不足: {balance} BNB < 0.01 BNB")
            
            logger.info(f"钱包余额: {balance:.6f} BNB")
            result['steps_completed'].append('balance_check')
            
            # 1. 创建代币
            logger.info("📝 创建代币...")
            token_config = self.create_token_config(wallet_num)
            
            # 随机选择图片
            selected_image = self._get_random_image()
            
            logger.info(f"代币配置: {token_config['name']} ({token_config['shortName']})")
            if selected_image:
                logger.info(f"使用图片: {os.path.basename(selected_image)}")
            
            create_result = bot.create_token_complete(
                token_config,
                image_path=selected_image,
                deploy_on_chain=True,
                purchase_amount=wallet_info['purchase_amount']
            )
            
            if not create_result.get('success'):
                raise Exception(f"代币创建失败: {create_result.get('error', '未知错误')}")
            
            result['token_address'] = create_result.get('token_address')
            result['token_name'] = token_config['name']
            result['token_symbol'] = token_config['shortName']
            result['image_used'] = os.path.basename(selected_image) if selected_image else 'None'
            result['create_tx'] = create_result.get('tx_hash')
            result['steps_completed'].append('token_created')
            
            logger.info(f"✅ 代币创建成功: {result['token_name']} ({result['token_symbol']}) - {result['token_address']}")
            
            # 2. 购买代币（如果指定了购买金额且未在创建时购买）
            if wallet_info['purchase_amount'] > 0:
                if 'purchase_tx' not in create_result:  # 创建时没有购买
                    logger.info(f"🛒 购买代币: {wallet_info['purchase_amount']} BNB")
                    buy_result = bot.blockchain_manager._buy_token(
                        result['token_address'], 
                        wallet_info['purchase_amount']
                    )
                    
                    if buy_result and buy_result.get('success'):
                        result['buy_tx'] = buy_result.get('tx_hash')
                        result['steps_completed'].append('token_bought')
                        logger.info(f"✅ 代币购买成功")
                    else:
                        logger.warning(f"⚠️ 代币购买失败: {buy_result.get('error') if buy_result else '未知错误'}")
                else:
                    result['buy_tx'] = create_result.get('purchase_tx')
                    result['steps_completed'].append('token_bought')
                    logger.info(f"✅ 代币已在创建时购买")
            
            # 3. 等待一段时间（让交易确认）
            if result['buy_tx']:
                logger.info("⏳ 等待交易确认...")
                time.sleep(10)
            
            # 4. 卖出代币（如果指定了卖出百分比且大于0）
            if wallet_info['sell_percentage'] > 0:
                logger.info(f"💰 卖出代币: {wallet_info['sell_percentage']}%")
                
                sell_result = bot.sell_token(
                    result['token_address'], 
                    wallet_info['sell_percentage']
                )
                
                if sell_result and sell_result.get('success'):
                    result['sell_tx'] = sell_result.get('tx_hash')
                    result['steps_completed'].append('token_sold')
                    logger.info(f"✅ 代币卖出成功")
                else:
                    logger.warning(f"⚠️ 代币卖出失败: {sell_result.get('error') if sell_result else '未知错误'}")
            
            result['success'] = True
            self.success_count += 1
            logger.info(f"🎉 钱包 {wallet_num} 处理完成")
            
        except Exception as e:
            result['error'] = str(e)
            self.failed_count += 1
            logger.error(f"❌ 钱包 {wallet_num} 处理失败: {e}")
        
        return result
    
    def run_batch(self, file_path: str, delay_between_wallets: int = 5) -> List[Dict[str, Any]]:
        """批量执行"""
        logger.info(f"🚀 开始批量执行，数据文件: {file_path}")
        
        # 加载钱包信息
        wallets = self.load_wallets_from_file(file_path)
        if not wallets:
            logger.error("没有有效的钱包信息")
            return []
        
        logger.info(f"准备处理 {len(wallets)} 个钱包")
        
        # 逐个处理钱包
        for i, wallet_info in enumerate(wallets, 1):
            result = self.process_wallet(wallet_info, i, len(wallets))
            self.results.append(result)
            
            # 钱包间延迟（避免API限制）
            if i < len(wallets) and delay_between_wallets > 0:
                logger.info(f"⏳ 等待 {delay_between_wallets} 秒后处理下一个钱包...")
                time.sleep(delay_between_wallets)
        
        # 生成报告
        self.generate_report()
        
        return self.results
    
    def generate_report(self):
        """生成执行报告"""
        logger.info("📊 生成执行报告...")
        
        # 控制台报告
        print("\n" + "="*80)
        print("📊 批量执行报告")
        print("="*80)
        print(f"总计钱包: {len(self.results)}")
        print(f"成功处理: {self.success_count}")
        print(f"失败处理: {self.failed_count}")
        print(f"成功率: {(self.success_count/len(self.results)*100):.1f}%" if self.results else "0%")
        
        print("\n📋 详细结果:")
        for result in self.results:
            status = "✅ 成功" if result['success'] else "❌ 失败"
            print(f"钱包 {result['wallet_num']}: {result['address'][:10]}...{result['address'][-6:]} - {status}")
            if result['token_name']:
                print(f"   代币名称: {result['token_name']} ({result['token_symbol']})")
            if result['token_address']:
                print(f"   代币地址: {result['token_address']}")
            if result['image_used']:
                print(f"   使用图片: {result['image_used']}")
            if result['create_tx']:
                print(f"   创建交易: {result['create_tx']}")
            if result['buy_tx']:
                print(f"   购买交易: {result['buy_tx']}")
            if result['sell_tx']:
                print(f"   卖出交易: {result['sell_tx']}")
            if result['error']:
                print(f"   错误信息: {result['error']}")
            print(f"   完成步骤: {', '.join(result['steps_completed'])}")
            print()
        
        # 保存CSV报告
        self.save_csv_report()
    
    def save_csv_report(self):
        """保存CSV报告"""
        timestamp = int(time.time())
        csv_file = f"logs/batch_report_{timestamp}.csv"
        
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    '钱包序号', '钱包地址', '处理状态', '代币名称', '代币符号', '代币地址',
                    '使用图片', '创建交易', '购买交易', '卖出交易', '完成步骤', '错误信息'
                ])
                
                for result in self.results:
                    writer.writerow([
                        result['wallet_num'],
                        result['address'],
                        '成功' if result['success'] else '失败',
                        result['token_name'] or '',
                        result['token_symbol'] or '',
                        result['token_address'] or '',
                        result['image_used'] or '',
                        result['create_tx'] or '',
                        result['buy_tx'] or '',
                        result['sell_tx'] or '',
                        ', '.join(result['steps_completed']),
                        result['error'] or ''
                    ])
            
            logger.info(f"📄 CSV报告已保存: {csv_file}")
        except Exception as e:
            logger.error(f"保存CSV报告失败: {e}")

def main():
    """主函数"""
    print("🚀 Four.meme 批量执行脚本")
    print("="*50)
    
    # 默认配置
    default_files = ["test_wallets.txt", "wallets.txt", "wallets_example.txt"]
    default_images = ["test_images", "token_images", "images"]
    
    # 自动查找数据文件
    file_path = None
    for default_file in default_files:
        if os.path.exists(default_file):
            file_path = default_file
            break
    
    if not file_path:
        print("❌ 未找到默认数据文件，请确保存在以下文件之一:")
        for f in default_files:
            print(f"   - {f}")
        return
    
    # 自动查找图片文件夹
    images_folder = None
    for default_img in default_images:
        if os.path.exists(default_img):
            images_folder = default_img
            break
    
    # 显示配置
    print(f"\n📋 自动检测配置:")
    print(f"   数据文件: {file_path}")
    print(f"   图片文件夹: {images_folder if images_folder else '不使用图片'}")
    
    # 用户输入延迟时间
    while True:
        try:
            delay_input = input(f"\n⏱️  请输入钱包间延迟时间 (秒，默认5): ").strip()
            if not delay_input:
                delay = 5
                break
            delay = int(delay_input)
            if delay < 0:
                print("❌ 延迟时间不能为负数，请重新输入")
                continue
            break
        except ValueError:
            print("❌ 请输入有效的数字")
            continue
    
    print(f"   钱包间延迟: {delay} 秒")
    
    confirm = input("\n确认开始批量执行? (y/n): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("❌ 用户取消执行")
        return
    
    # 创建执行器并运行
    runner = BatchRunner(images_folder)
    try:
        runner.run_batch(file_path, delay)
        print("\n🎉 批量执行完成！")
    except KeyboardInterrupt:
        print("\n👋 用户中断执行")
    except Exception as e:
        print(f"\n❌ 执行过程出现异常: {e}")
        logger.exception("批量执行异常")

if __name__ == "__main__":
    main() 