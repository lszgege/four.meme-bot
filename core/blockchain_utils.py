#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Four.meme 区块链交互工具
"""

import json
import time
from typing import Dict, Any, Optional
from web3 import Web3
from web3.middleware import geth_poa_middleware
import logging

logger = logging.getLogger(__name__)


class BlockchainManager:
    """区块链交互管理器"""
    
    # BSC 网络配置
    BSC_RPC_URLS = [
        "https://bsc-dataseed1.binance.org/",
        "https://bsc-dataseed2.binance.org/",
        "https://bsc-dataseed3.binance.org/",
        "https://bsc-dataseed4.binance.org/"
    ]
    
    # TokenManagerHelper3 合约地址 - BSC主网
    # 来源: Four.meme官方API文档
    TOKEN_MANAGER_ADDRESS = "0x5c952063c7fc8610FFDB798152D69F0B9550762b"
    
    # TokenManager2 合约ABI - 从真实的ABI文件加载
    @classmethod
    def load_abi(cls):
        """从ABI文件加载合约ABI"""
        try:
            # 尝试多个可能的ABI文件路径
            abi_paths = [
                "contracts/TokenManager2.lite.abi",
                "TokenManager2.lite.abi",
                "../contracts/TokenManager2.lite.abi"
            ]
            
            for abi_file in abi_paths:
                try:
                    with open(abi_file, 'r') as f:
                        logger.info(f"成功加载ABI文件: {abi_file}")
                        return json.load(f)
                except FileNotFoundError:
                    continue
            
            logger.error(f"所有ABI文件路径都不存在: {abi_paths}")
            raise FileNotFoundError("无法找到TokenManager2.lite.abi文件")
        except Exception as e:
            logger.error(f"无法加载ABI文件: {e}")
            # 返回基本的createToken函数ABI作为后备
            return [
                {
                    "inputs": [
                        {"internalType": "bytes", "name": "args", "type": "bytes"},
                        {"internalType": "bytes", "name": "signature", "type": "bytes"}
                    ],
                    "name": "createToken",
                    "outputs": [],
                    "stateMutability": "payable",
                    "type": "function"
                }
            ]
    
    def __init__(self, private_key: str, rpc_url: Optional[str] = None):
        """
        初始化区块链管理器
        
        Args:
            private_key: 钱包私钥
            rpc_url: RPC节点URL，默认使用BSC主网
        """
        self.private_key = private_key
        self.rpc_url = rpc_url or self.BSC_RPC_URLS[0]
        self.web3 = None
        self.account = None
        self.contract = None
        
        self._initialize_connection()
    
    def _initialize_connection(self):
        """初始化Web3连接"""
        try:
            # 创建Web3实例
            self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            # 添加POA中间件（BSC需要）
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # 验证连接
            if not self.web3.is_connected():
                raise Exception("无法连接到区块链网络")
            
            # 设置账户
            self.account = self.web3.eth.account.from_key(self.private_key)
            
            # 创建合约实例
            contract_abi = self.load_abi()
            self.contract = self.web3.eth.contract(
                address=self.TOKEN_MANAGER_ADDRESS,
                abi=contract_abi
            )
            
            logger.info(f"TokenManager2合约地址: {self.TOKEN_MANAGER_ADDRESS}")
            
            logger.info(f"区块链连接成功: {self.rpc_url}")
            logger.info(f"钱包地址: {self.account.address}")
            logger.info(f"当前区块高度: {self.web3.eth.block_number}")
            
        except Exception as e:
            logger.error(f"初始化区块链连接失败: {e}")
            raise
    
    def get_balance(self) -> float:
        """
        获取钱包BNB余额
        
        Returns:
            BNB余额
        """
        try:
            balance_wei = self.web3.eth.get_balance(self.account.address)
            balance_bnb = self.web3.from_wei(balance_wei, 'ether')
            return float(balance_bnb)
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
            raise
    
    def estimate_gas(self, args: bytes, signature: bytes, purchase_value_wei: int) -> int:
        """
        估算创建代币的Gas费用
        
        Args:
            args: 创建参数字节数组
            signature: 签名字节数组
            purchase_value_wei: 购买代币的BNB数量（Wei）
            
        Returns:
            估算的Gas数量
        """
        try:
            if not self.contract:
                # 如果没有合约实例，返回默认Gas估算
                logger.warning("无合约实例，使用默认Gas估算")
                return 500000  # 默认50万Gas
                
            gas_estimate = self.contract.functions.createToken(
                args, signature
            ).estimate_gas({
                'from': self.account.address,
                'value': purchase_value_wei
            })
            
            logger.info(f"估算Gas: {gas_estimate}")
            return gas_estimate
            
        except Exception as e:
            logger.error(f"Gas估算失败: {e}")
            # 返回默认值而不是抛出异常
            return 500000
    
    def get_gas_price(self) -> int:
        """
        获取当前Gas价格
        
        Returns:
            Gas价格 (Wei)
        """
        try:
            gas_price = self.web3.eth.gas_price
            logger.info(f"当前Gas价格: {self.web3.from_wei(gas_price, 'gwei')} Gwei")
            return gas_price
        except Exception as e:
            logger.error(f"获取Gas价格失败: {e}")
            raise
    
    def create_token_on_chain(
        self, 
        create_arg: str, 
        signature: str,
        purchase_amount: float = 0.0,  # 购买代币的BNB数量
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        在区块链上创建代币，并可选择购买代币
        
        Args:
            create_arg: API返回的创建参数（hex字符串）
            signature: API返回的签名（hex字符串）
            purchase_amount: 购买代币的BNB数量（0表示仅创建不购买）
            gas_limit: Gas限制
            gas_price: Gas价格
            
        Returns:
            交易结果
        """
        try:
            if not self.contract:
                raise Exception("合约实例未初始化，请检查合约地址")
            
            # 第一步：创建代币
            logger.info("第一步：创建代币合约...")
            create_result = self._create_token_only(create_arg, signature, gas_limit, gas_price)
            
            if not create_result.get("success"):
                return create_result
            
            token_address = create_result.get("token_address")
            if not token_address:
                logger.error("创建代币成功但未获取到代币地址")
                return {
                    'success': False,
                    'error': '未获取到代币地址'
                }
            
            # 第二步：购买代币（如果指定了购买金额）
            if purchase_amount > 0:
                logger.info(f"第二步：购买 {purchase_amount} BNB 的代币...")
                buy_result = self._buy_token(token_address, purchase_amount, gas_price)
                
                # 合并结果
                result = {
                    'success': buy_result.get("success", False),
                    'tx_hash': create_result.get("tx_hash"),  # 创建交易的哈希
                    'buy_tx_hash': buy_result.get("tx_hash"),  # 购买交易的哈希
                    'block_number': create_result.get("block_number"),
                    'gas_used': create_result.get("gas_used") + buy_result.get("gas_used", 0),
                    'token_address': token_address,
                    'purchase_amount': purchase_amount,
                    'create_receipt': create_result.get("receipt"),
                    'buy_receipt': buy_result.get("receipt")
                }
                
                if buy_result.get("success"):
                    logger.info(f"代币创建并购买成功: {token_address}, 购买了 {purchase_amount} BNB")
                else:
                    logger.error(f"代币创建成功但购买失败: {buy_result.get('error')}")
                    result['error'] = f"创建成功但购买失败: {buy_result.get('error')}"
                
                return result
            else:
                # 仅创建，不购买
                logger.info(f"代币创建成功: {token_address}")
                return create_result
            
        except Exception as e:
            logger.error(f"区块链操作失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_token_only(
        self, 
        create_arg: str, 
        signature: str,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        仅创建代币，不购买
        """
        try:
            # 转换hex字符串为bytes
            args_bytes = bytes.fromhex(create_arg.replace('0x', ''))
            signature_bytes = bytes.fromhex(signature.replace('0x', ''))
            
            logger.info(f"准备调用createToken，参数长度: args={len(args_bytes)}, signature={len(signature_bytes)}")
            
            # 获取当前nonce
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            
            # 估算Gas（如果未提供）
            if not gas_limit:
                gas_limit = self.estimate_gas(args_bytes, signature_bytes, 0)  # 创建时不发送BNB
                gas_limit = int(gas_limit * 1.2)  # 增加20%余量
            
            # 获取Gas价格（如果未提供）
            if not gas_price:
                gas_price = self.get_gas_price()
                gas_price = int(gas_price * 1.1)  # 增加10%以加快确认
            
            # 构建交易 - 仅创建，不发送BNB
            transaction = self.contract.functions.createToken(
                args_bytes, signature_bytes
            ).build_transaction({
                'from': self.account.address,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
                'value': 0  # 创建时不发送BNB
            })
            
            logger.info(f"构建创建交易: Gas={gas_limit}, GasPrice={self.web3.from_wei(gas_price, 'gwei')} Gwei")
            
            # 签名交易
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            
            # 发送交易
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.info(f"创建交易已发送: {tx_hash_hex}")
            
            # 等待交易确认
            receipt = self.wait_for_transaction(tx_hash)
            
            # 解析创建的代币地址
            token_address = self.parse_token_address_from_receipt(receipt)
            
            return {
                'success': True,
                'tx_hash': tx_hash_hex,
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'token_address': token_address,
                'receipt': receipt
            }
            
        except Exception as e:
            logger.error(f"创建代币失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _buy_token(
        self, 
        token_address: str, 
        purchase_amount: float,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        购买指定代币
        
        Args:
            token_address: 代币合约地址
            purchase_amount: 购买金额（BNB）
            gas_price: Gas价格
            
        Returns:
            购买结果
        """
        try:
            purchase_value_wei = self.web3.to_wei(purchase_amount, 'ether')
            
            # 获取当前nonce（包含pending交易）
            nonce = self.web3.eth.get_transaction_count(self.account.address, 'pending')
            
            # 获取Gas价格（如果未提供）
            if not gas_price:
                gas_price = self.get_gas_price()
                gas_price = int(gas_price * 1.1)
            
            # 使用buyTokenAMAP方法（As Much As Possible - 用指定的BNB购买尽可能多的代币）
            # buyTokenAMAP(address token, uint256 funds, uint256 minAmount)
            transaction = self.contract.functions.buyTokenAMAP(
                token_address,
                purchase_value_wei,  # funds - 要花费的BNB数量
                0  # minAmount - 最少获得的代币数量，设为0表示接受任何数量
            ).build_transaction({
                'from': self.account.address,
                'gas': 300000,  # 购买交易的Gas限制
                'gasPrice': gas_price,
                'nonce': nonce,
                'value': purchase_value_wei  # 发送的BNB数量
            })
            
            logger.info(f"构建购买交易: 代币={token_address}, 金额={purchase_amount} BNB")
            
            # 签名交易
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            
            # 发送交易
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.info(f"购买交易已发送: {tx_hash_hex}")
            
            # 等待交易确认
            receipt = self.wait_for_transaction(tx_hash)
            
            return {
                'success': True,
                'tx_hash': tx_hash_hex,
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'receipt': receipt
            }
            
        except Exception as e:
            logger.error(f"购买代币失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def wait_for_transaction(self, tx_hash, timeout: int = 300) -> Dict[str, Any]:
        """
        等待交易确认
        
        Args:
            tx_hash: 交易哈希
            timeout: 超时时间（秒）
            
        Returns:
            交易收据
        """
        try:
            logger.info(f"等待交易确认: {tx_hash.hex()}")
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            
            if receipt['status'] == 1:
                logger.info(f"交易确认成功: 区块 {receipt['blockNumber']}, Gas使用 {receipt['gasUsed']}")
            else:
                logger.error(f"交易失败: {receipt}")
                raise Exception("交易执行失败")
            
            return receipt
            
        except Exception as e:
            logger.error(f"等待交易确认失败: {e}")
            raise
    
    def parse_token_address_from_receipt(self, receipt: Dict[str, Any]) -> Optional[str]:
        """
        从交易收据中解析创建的代币地址
        
        Args:
            receipt: 交易收据
            
        Returns:
            代币合约地址
        """
        try:
            # 解析TokenCreate事件（ABI中的事件名称是TokenCreate）
            logs = self.contract.events.TokenCreate().process_receipt(receipt)
            
            if logs:
                token_address = logs[0]['args']['token']  # 根据ABI，参数名是token，不是tokenAddress
                logger.info(f"解析到代币地址: {token_address}")
                return token_address
            else:
                logger.warning("未找到TokenCreate事件")
                return None
                
        except Exception as e:
            logger.error(f"解析代币地址失败: {e}")
            return None
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        获取交易状态
        
        Args:
            tx_hash: 交易哈希
            
        Returns:
            交易状态信息
        """
        try:
            # 获取交易信息
            tx = self.web3.eth.get_transaction(tx_hash)
            
            # 尝试获取交易收据
            try:
                receipt = self.web3.eth.get_transaction_receipt(tx_hash)
                status = "成功" if receipt['status'] == 1 else "失败"
                confirmed = True
            except:
                receipt = None
                status = "待确认"
                confirmed = False
            
            return {
                'hash': tx_hash,
                'status': status,
                'confirmed': confirmed,
                'block_number': receipt['blockNumber'] if receipt else None,
                'gas_used': receipt['gasUsed'] if receipt else None,
                'transaction': tx,
                'receipt': receipt
            }
            
        except Exception as e:
            logger.error(f"获取交易状态失败: {e}")
            return {
                'hash': tx_hash,
                'status': "错误",
                'error': str(e)
            }
    
    def switch_rpc_node(self):
        """切换到下一个RPC节点"""
        try:
            current_index = self.BSC_RPC_URLS.index(self.rpc_url)
            next_index = (current_index + 1) % len(self.BSC_RPC_URLS)
            self.rpc_url = self.BSC_RPC_URLS[next_index]
            
            logger.info(f"切换RPC节点: {self.rpc_url}")
            self._initialize_connection()
            
        except Exception as e:
            logger.error(f"切换RPC节点失败: {e}")
            raise

    def get_token_balance(self, token_address: str) -> float:
        """
        获取指定代币的余额
        
        Args:
            token_address: 代币合约地址
            
        Returns:
            代币余额（以代币单位计算）
        """
        try:
            # 确保地址是checksum格式
            token_address = self.web3.to_checksum_address(token_address)
            
            # 创建代币合约实例（使用标准ERC20 ABI的balanceOf方法）
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }
            ]
            
            token_contract = self.web3.eth.contract(
                address=token_address,
                abi=erc20_abi
            )
            
            # 获取余额和精度
            balance_wei = token_contract.functions.balanceOf(self.account.address).call()
            decimals = token_contract.functions.decimals().call()
            
            # 转换为代币单位
            balance = balance_wei / (10 ** decimals)
            
            logger.info(f"代币余额: {balance} tokens (地址: {token_address})")
            return balance
            
        except Exception as e:
            logger.error(f"获取代币余额失败: {e}")
            return 0.0
    
    def get_token_status(self, token_address: str) -> Dict[str, Any]:
        """
        获取代币的交易状态
        
        Args:
            token_address: 代币合约地址
            
        Returns:
            代币状态信息
        """
        try:
            # 确保地址是checksum格式
            token_address = self.web3.to_checksum_address(token_address)
            
            # 获取代币信息，包含状态
            token_info = self.contract.functions._tokenInfos(token_address).call()
            
            # 解析状态
            status_code = token_info[12]  # status字段是第13个元素（索引12）
            
            # 获取状态常量
            status_trading = self.contract.functions.STATUS_TRADING().call()
            status_completed = self.contract.functions.STATUS_COMPLETED().call()
            status_halt = self.contract.functions.STATUS_HALT().call()
            status_adding_liquidity = self.contract.functions.STATUS_ADDING_LIQUIDITY().call()
            
            # 判断状态
            if status_code == status_trading:
                status_name = "TRADING"
                can_trade = True
            elif status_code == status_completed:
                status_name = "COMPLETED"
                can_trade = False
            elif status_code == status_halt:
                status_name = "HALT"
                can_trade = False
            elif status_code == status_adding_liquidity:
                status_name = "ADDING_LIQUIDITY"
                can_trade = False
            else:
                status_name = f"UNKNOWN({status_code})"
                can_trade = False
            
            result = {
                'success': True,
                'status_code': status_code,
                'status_name': status_name,
                'can_trade': can_trade,
                'token_info': {
                    'base': token_info[0],
                    'quote': token_info[1],
                    'template': token_info[2],
                    'totalSupply': token_info[3],
                    'maxOffers': token_info[4],
                    'maxRaising': token_info[5],
                    'launchTime': token_info[6],
                    'offers': token_info[7],
                    'funds': token_info[8],
                    'lastPrice': token_info[9],
                    'K': token_info[10],
                    'T': token_info[11],
                    'status': token_info[12]
                }
            }
            
            logger.info(f"代币状态: {status_name} (代码: {status_code}), 可交易: {can_trade}")
            return result
            
        except Exception as e:
            logger.error(f"获取代币状态失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _sell_token(
        self, 
        token_address: str, 
        amount: float,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        卖出指定数量的代币
        
        Args:
            token_address: 代币合约地址
            amount: 卖出的代币数量
            gas_price: Gas价格
            
        Returns:
            卖出结果
        """
        try:
            # 确保地址是checksum格式
            token_address = self.web3.to_checksum_address(token_address)
            
            # 获取代币精度
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }
            ]
            
            token_contract = self.web3.eth.contract(
                address=token_address,
                abi=erc20_abi
            )
            
            decimals = token_contract.functions.decimals().call()
            amount_wei = int(amount * (10 ** decimals))
            
            # 重要：确保数量是合适的倍数（参考别人的代码）
            if decimals == 18:
                amount_wei = (amount_wei // 1000000000) * 1000000000
            
            logger.info(f"准备卖出: {amount} tokens = {amount_wei} wei (调整后)")
            
            # 获取当前nonce（包含pending交易）
            nonce = self.web3.eth.get_transaction_count(self.account.address, 'pending')
            
            # 获取Gas价格（如果未提供）
            if not gas_price:
                gas_price = self.get_gas_price()
                gas_price = int(gas_price * 1.1)
            
            # 使用正确的2参数版本：sellToken(address tokenAddress, uint256 amount)
            # 这是 TokenManager V2 的标准方法，不需要 origin 和 minFunds
            transaction = self.contract.functions.sellToken(
                token_address,  # tokenAddress
                amount_wei      # amount - 要卖出的代币数量（wei单位）
            ).build_transaction({
                'from': self.account.address,
                'gas': 1000000,  # 使用和成功交易相同的Gas限制
                'gasPrice': gas_price,
                'nonce': nonce,
                'value': 0  # 卖出不需要发送BNB
            })
            
            logger.info(f"构建卖出交易: 代币={token_address}, 数量={amount} tokens")
            
            # 签名交易
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            
            # 发送交易
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.info(f"卖出交易已发送: {tx_hash_hex}")
            
            # 等待交易确认
            receipt = self.wait_for_transaction(tx_hash)
            
            return {
                'success': True,
                'tx_hash': tx_hash_hex,
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'receipt': receipt
            }
            
        except Exception as e:
            logger.error(f"卖出代币失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sell_token_complete(
        self,
        token_address: str,
        sell_percentage: float = 100.0,  # 卖出百分比，默认100%（全部卖出）
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        完整的卖出流程：检查余额 -> 计算卖出数量 -> 执行卖出
        
        Args:
            token_address: 代币合约地址
            sell_percentage: 卖出百分比（1-100）
            gas_price: Gas价格
            
        Returns:
            完整的卖出结果
        """
        try:
            logger.info(f"开始卖出代币流程: {token_address}")
            
            # 1. 检查代币状态
            status_result = self.get_token_status(token_address)
            if not status_result.get('success'):
                return {
                    'success': False,
                    'error': f"无法获取代币状态: {status_result.get('error')}"
                }
            
            if not status_result.get('can_trade'):
                return {
                    'success': False,
                    'error': f"代币当前状态不允许交易: {status_result.get('status_name')}"
                }
            
            # 2. 获取代币余额
            balance = self.get_token_balance(token_address)
            if balance <= 0:
                return {
                    'success': False,
                    'error': '代币余额为0，无法卖出'
                }
            
            # 3. 计算卖出数量
            if sell_percentage <= 0 or sell_percentage > 100:
                return {
                    'success': False,
                    'error': '卖出百分比必须在1-100之间'
                }
            
            sell_amount = balance * (sell_percentage / 100)
            logger.info(f"代币余额: {balance}, 卖出比例: {sell_percentage}%, 卖出数量: {sell_amount}")
            logger.info(f"代币状态: {status_result.get('status_name')}, 可交易: {status_result.get('can_trade')}")
            
            # 4. 先授权代币
            logger.info("步骤3a: 授权代币给TokenManager合约")
            approve_result = self.approve_token(token_address, sell_amount, gas_price)
            if not approve_result.get('success'):
                return {
                    'success': False,
                    'error': f"代币授权失败: {approve_result.get('error')}"
                }
            logger.info("代币授权成功")
            
            # 5. 执行卖出
            logger.info("步骤3b: 执行卖出交易")
            sell_result = self._sell_token(token_address, sell_amount, gas_price)
            
            # 6. 合并结果
            result = {
                'success': sell_result.get('success', False),
                'token_address': token_address,
                'original_balance': balance,
                'sell_percentage': sell_percentage,
                'sell_amount': sell_amount,
                'approve_tx_hash': approve_result.get('tx_hash'),
                'tx_hash': sell_result.get('tx_hash'),
                'block_number': sell_result.get('block_number'),
                'gas_used': approve_result.get('gas_used', 0) + sell_result.get('gas_used', 0),
                'receipt': sell_result.get('receipt')
            }
            
            if sell_result.get('success'):
                logger.info(f"代币卖出成功: 卖出 {sell_amount} tokens ({sell_percentage}%)")
            else:
                result['error'] = sell_result.get('error')
                logger.error(f"代币卖出失败: {sell_result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"完整卖出流程失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }


    def approve_token(
        self,
        token_address: str,
        amount: float,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        授权代币给TokenManager合约
        
        Args:
            token_address: 代币合约地址
            amount: 授权数量
            gas_price: Gas价格
            
        Returns:
            授权结果
        """
        try:
            # 确保地址是checksum格式
            token_address = self.web3.to_checksum_address(token_address)
            
            # ERC20 approve方法的ABI
            erc20_abi = [
                {
                    "constant": False,
                    "inputs": [
                        {"name": "_spender", "type": "address"},
                        {"name": "_value", "type": "uint256"}
                    ],
                    "name": "approve",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }
            ]
            
            token_contract = self.web3.eth.contract(
                address=token_address,
                abi=erc20_abi
            )
            
            # 获取代币精度
            decimals = token_contract.functions.decimals().call()
            amount_wei = int(amount * (10 ** decimals))
            
            logger.info(f"准备授权: {amount} tokens = {amount_wei} wei 给 {self.TOKEN_MANAGER_ADDRESS}")
            
            # 获取当前nonce
            nonce = self.web3.eth.get_transaction_count(self.account.address, 'pending')
            
            # 获取Gas价格
            if not gas_price:
                gas_price = self.get_gas_price()
                gas_price = int(gas_price * 1.1)
            
            # 构建授权交易
            transaction = token_contract.functions.approve(
                self.TOKEN_MANAGER_ADDRESS,  # spender
                amount_wei  # amount
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,  # 授权交易的Gas限制
                'gasPrice': gas_price,
                'nonce': nonce,
                'value': 0
            })
            
            logger.info(f"构建授权交易: 代币={token_address}, 数量={amount} tokens")
            
            # 签名交易
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            
            # 发送交易
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.info(f"授权交易已发送: {tx_hash_hex}")
            
            # 等待交易确认
            receipt = self.wait_for_transaction(tx_hash)
            
            return {
                'success': True,
                'tx_hash': tx_hash_hex,
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'receipt': receipt
            }
            
        except Exception as e:
            logger.error(f"授权代币失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _sell_token_via_pancakeswap(
        self, 
        token_address: str, 
        amount: float,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        通过PancakeSwap路由卖出代币
        
        Args:
            token_address: 代币合约地址
            amount: 卖出的代币数量
            gas_price: Gas价格
            
        Returns:
            卖出结果
        """
        try:
            # PancakeSwap V2 Router地址
            PANCAKESWAP_ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
            WBNB_ADDRESS = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
            
            # 确保地址是checksum格式
            token_address = self.web3.to_checksum_address(token_address)
            
            # PancakeSwap Router ABI (简化版本)
            router_abi = [
                {
                    "inputs": [
                        {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                        {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                        {"internalType": "address[]", "name": "path", "type": "address[]"},
                        {"internalType": "address", "name": "to", "type": "address"},
                        {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                    ],
                    "name": "swapExactTokensForETH",
                    "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            
            router_contract = self.web3.eth.contract(
                address=PANCAKESWAP_ROUTER,
                abi=router_abi
            )
            
            # 获取代币精度
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }
            ]
            
            token_contract = self.web3.eth.contract(
                address=token_address,
                abi=erc20_abi
            )
            
            decimals = token_contract.functions.decimals().call()
            amount_wei = int(amount * (10 ** decimals))
            
            logger.info(f"准备通过PancakeSwap卖出: {amount} tokens = {amount_wei} wei")
            
            # 获取当前nonce
            nonce = self.web3.eth.get_transaction_count(self.account.address, 'pending')
            
            # 获取Gas价格
            if not gas_price:
                gas_price = self.get_gas_price()
                gas_price = int(gas_price * 1.1)
            
            # 设置交易路径：Token -> WBNB
            path = [token_address, WBNB_ADDRESS]
            
            # 设置截止时间（当前时间 + 20分钟）
            deadline = int(time.time()) + 1200
            
            # 构建交易：swapExactTokensForETH
            transaction = router_contract.functions.swapExactTokensForETH(
                amount_wei,  # amountIn - 要卖出的代币数量
                0,  # amountOutMin - 最少获得的BNB数量，设为0表示接受任何数量
                path,  # path - 交易路径
                self.account.address,  # to - 接收地址
                deadline  # deadline - 截止时间
            ).build_transaction({
                'from': self.account.address,
                'gas': 300000,  # 卖出交易的Gas限制
                'gasPrice': gas_price,
                'nonce': nonce,
                'value': 0  # 卖出不需要发送BNB
            })
            
            logger.info(f"构建PancakeSwap卖出交易: 代币={token_address}, 数量={amount} tokens")
            
            # 签名交易
            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            
            # 发送交易
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.info(f"PancakeSwap卖出交易已发送: {tx_hash_hex}")
            
            # 等待交易确认
            receipt = self.wait_for_transaction(tx_hash)
            
            return {
                'success': True,
                'tx_hash': tx_hash_hex,
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'receipt': receipt,
                'method': 'PancakeSwap'
            }
            
        except Exception as e:
            logger.error(f"通过PancakeSwap卖出代币失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'PancakeSwap'
            }


def bytes_to_hex(data: bytes) -> str:
    """将bytes转换为hex字符串"""
    return '0x' + data.hex()

def hex_to_bytes(hex_str: str) -> bytes:
    """将hex字符串转换为bytes"""
    return bytes.fromhex(hex_str.replace('0x', ''))

if __name__ == "__main__":
    # 测试区块链连接
    print("测试区块链连接...")
    
    # 注意：这里需要实际的私钥和合约地址
    try:
        private_key = "your_private_key_here"
        manager = BlockchainManager(private_key)
        
        balance = manager.get_balance()
        print(f"钱包余额: {balance} BNB")
        
        gas_price = manager.get_gas_price()
        print(f"当前Gas价格: {manager.web3.from_wei(gas_price, 'gwei')} Gwei")
        
    except Exception as e:
        print(f"测试失败: {e}") 