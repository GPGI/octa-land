"""
SARAKT BLOCKCHAIN INTEGRATION - Python
Свързва Universe Engine със Smart Contract чрез Web3.py
"""

from web3 import Web3
from eth_account import Account
from typing import Dict, Optional, List, Tuple
import json
import os
from dotenv import load_dotenv

# Импорт на Universe Engine
from sarakt_universe_engine import SaraktUniverse, NPC, StructureType

load_dotenv()


# ============================================
# BLOCKCHAIN CONNECTOR
# ============================================

class BlockchainConnector:
    """Свързва се със Smart Contract на Avalanche Subnet"""
    
    def __init__(self, config: Dict):
        self.rpc_url = config['rpc_url']
        self.contract_address = config['contract_address']
        self.private_key = config['private_key']
        
        # Инициализира Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Проверява връзката
        if not self.w3.is_connected():
            raise ConnectionError(f"Не може да се свърже с {self.rpc_url}")
        
        # Настройва акаунт
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address
        
        # Зарежда ABI и създава contract instance
        self.contract_abi = self._get_contract_abi()
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=self.contract_abi
        )
        
        self.pending_transactions = []
        self.minted_assets = {}
        
        print(f"✅ Blockchain свързан: {self.address}")
    
    def _get_contract_abi(self) -> List:
        """Връща ABI на contract-а"""
        # Опростен ABI - само функциите които ни трябват
        return [
            {
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "plotNumber", "type": "uint256"},
                    {"name": "zone", "type": "string"}
                ],
                "name": "mintOctaviaPlot",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "plotTokenId", "type": "uint256"},
                    {"name": "structureType", "type": "uint8"}
                ],
                "name": "buildStructure",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "planetId", "type": "uint256"},
                    {"name": "npcName", "type": "string"},
                    {"name": "initialOwner", "type": "address"}
                ],
                "name": "spawnNPC",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "npcTokenId", "type": "uint256"},
                    {"name": "player", "type": "address"},
                    {"name": "loyaltyChange", "type": "uint256"},
                    {"name": "isIncrease", "type": "bool"}
                ],
                "name": "updateNPCLoyalty",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "name", "type": "string"},
                    {"name": "leader", "type": "address"}
                ],
                "name": "createFaction",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "planetId", "type": "uint256"},
                    {"name": "resourceType", "type": "string"},
                    {"name": "amount", "type": "uint256"},
                    {"name": "extractor", "type": "address"}
                ],
                "name": "extractPlanetaryResource",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "account", "type": "address"},
                    {"name": "id", "type": "uint256"}
                ],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def mint_plot_nft(self, player_id: str, plot_number: int, zone: str) -> Dict:
        """Минтва парцел като NFT"""
        try:
            print(f"⛓️  Минтване на парцел #{plot_number} ({zone}) за {player_id}...")
            
            # Подготовка на транзакция
            function = self.contract.functions.mintOctaviaPlot(
                Web3.to_checksum_address(player_id),
                plot_number,
                zone
            )
            
            # Изпраща транзакцията
            tx_hash = self._send_transaction(function)
            
            # Чака за потвърждение
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Извлича token ID от receipt
            token_id = self._extract_token_id_from_receipt(receipt)
            
            self.minted_assets[f'plot_{plot_number}'] = {
                'token_id': token_id,
                'owner': player_id,
                'type': 'LAND_PLOT',
                'tx_hash': receipt['transactionHash'].hex()
            }
            
            print(f"✅ Парцел минтнат! Token ID: {token_id}")
            return {
                'token_id': token_id,
                'tx_hash': receipt['transactionHash'].hex()
            }
            
        except Exception as e:
            print(f"❌ Грешка при минтване: {str(e)}")
            raise
    
    def build_structure_on_chain(self, plot_token_id: int, structure_type: StructureType) -> Dict:
        """Строи структура на парцел (on-chain)"""
        try:
            print(f"🏗️  Строене на {structure_type.name} на парцел token {plot_token_id}...")
            
            function = self.contract.functions.buildStructure(
                plot_token_id,
                structure_type.value
            )
            
            tx_hash = self._send_transaction(function)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            print(f"✅ Структура построена! TX: {receipt['transactionHash'].hex()}")
            return {'tx_hash': receipt['transactionHash'].hex()}
            
        except Exception as e:
            print(f"❌ Грешка при строене: {str(e)}")
            raise
    
    def mint_npc_nft(self, npc: NPC, initial_owner: str) -> Dict:
        """Минтва NPC като NFT"""
        try:
            print(f"👤 Минтване на NPC: {npc.get_name()} (ID: {npc.id})...")
            
            function = self.contract.functions.spawnNPC(
                npc.planet_id,
                npc.get_name(),
                Web3.to_checksum_address(initial_owner)
            )
            
            tx_hash = self._send_transaction(function)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            token_id = self._extract_token_id_from_receipt(receipt)
            
            self.minted_assets[f'npc_{npc.id}'] = {
                'token_id': token_id,
                'owner': initial_owner,
                'type': 'NPC',
                'npc_data': npc.get_status(),
                'tx_hash': receipt['transactionHash'].hex()
            }
            
            print(f"✅ NPC минтнат! Token ID: {token_id}")
            return {
                'token_id': token_id,
                'tx_hash': receipt['transactionHash'].hex()
            }
            
        except Exception as e:
            print(f"❌ Грешка при минтване на NPC: {str(e)}")
            raise
    
    def sync_npc_loyalty(self, npc_token_id: int, player_id: str, 
                        current_loyalty: float, previous_loyalty: float) -> Dict:
        """Синхронизира лоялност на NPC on-chain"""
        try:
            is_increase = current_loyalty > previous_loyalty
            loyalty_change = abs(current_loyalty - previous_loyalty)
            
            if loyalty_change == 0:
                return {}
            
            print(f"💝 Актуализиране на NPC {npc_token_id} лоялност: {previous_loyalty:.1f} → {current_loyalty:.1f}")
            
            function = self.contract.functions.updateNPCLoyalty(
                npc_token_id,
                Web3.to_checksum_address(player_id),
                int(loyalty_change),
                is_increase
            )
            
            tx_hash = self._send_transaction(function)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            print(f"✅ Лоялност синхронизирана! TX: {receipt['transactionHash'].hex()}")
            return {'tx_hash': receipt['transactionHash'].hex()}
            
        except Exception as e:
            print(f"❌ Грешка при синхронизация на лоялност: {str(e)}")
            raise
    
    def create_faction_nft(self, faction_name: str, leader_address: str) -> Dict:
        """Създава faction като NFT"""
        try:
            print(f"🏢 Създаване на faction: {faction_name}...")
            
            function = self.contract.functions.createFaction(
                faction_name,
                Web3.to_checksum_address(leader_address)
            )
            
            tx_hash = self._send_transaction(function)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            faction_id = self._extract_token_id_from_receipt(receipt)
            
            print(f"✅ Faction създаден! ID: {faction_id}")
            return {
                'faction_id': faction_id,
                'tx_hash': receipt['transactionHash'].hex()
            }
            
        except Exception as e:
            print(f"❌ Грешка при създаване на faction: {str(e)}")
            raise
    
    def extract_and_sync_resource(self, planet_id: int, resource_type: str,
                                  amount: int, extractor_address: str) -> Dict:
        """Извлича ресурс и синхронизира on-chain"""
        try:
            print(f"⛏️  Извличане на {amount} {resource_type} от планета {planet_id}...")
            
            function = self.contract.functions.extractPlanetaryResource(
                planet_id,
                resource_type,
                amount,
                Web3.to_checksum_address(extractor_address)
            )
            
            tx_hash = self._send_transaction(function)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            print(f"✅ Ресурс извлечен! TX: {receipt['transactionHash'].hex()}")
            return {'tx_hash': receipt['transactionHash'].hex()}
            
        except Exception as e:
            print(f"❌ Грешка при извличане на ресурс: {str(e)}")
            raise
    
    def check_ownership(self, address: str, token_id: int) -> bool:
        """Проверява собственост върху NFT"""
        try:
            balance = self.contract.functions.balanceOf(
                Web3.to_checksum_address(address),
                token_id
            ).call()
            return balance > 0
        except Exception as e:
            print(f"❌ Грешка при проверка на собственост: {str(e)}")
            return False
    
    def _send_transaction(self, function) -> str:
        """Изпраща транзакция"""
        # Построява транзакция
        tx = function.build_transaction({
            'from': self.address,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'gas': 2000000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Подписва транзакцията
        signed_tx = self.account.sign_transaction(tx)
        
        # Изпраща транзакцията
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return tx_hash
    
    def _extract_token_id_from_receipt(self, receipt) -> int:
        """Извлича token ID от transaction receipt"""
        # Търси в logs за AssetCreated event
        for log in receipt['logs']:
            if len(log['topics']) > 1:
                # Token ID обикновено е във втория topic
                return int(log['topics'][1].hex(), 16)
        return 0
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        """Проверява статус на транзакция"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                'status': 'success' if receipt['status'] == 1 else 'failed',
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed']
            }
        except Exception:
            return {'status': 'pending'}


# ============================================
# UNIVERSE-BLOCKCHAIN BRIDGE
# ============================================

class SaraktBridge:
    """Мост между Universe Engine и Blockchain"""
    
    def __init__(self, universe: SaraktUniverse, blockchain: BlockchainConnector):
        self.universe = universe
        self.blockchain = blockchain
        self.sync_queue = []
        self.auto_sync = True
        
        # Проследява синхронизирани активи
        self.synced_assets = {
            'plots': set(),
            'npcs': set(),
            'structures': set(),
            'resources': set()
        }
    
    def claim_plot(self, player_id: str, plot_number: int) -> Dict:
        """Играч претендира парцел"""
        try:
            city = self.universe.get_city('Octavia Capital City')
            plot = next((p for p in city.plots if p.id == plot_number), None)
            
            if not plot:
                raise ValueError('Парцел не е намерен')
            if plot.owner:
                raise ValueError('Парцел вече е зает')
            
            # 1. Актуализира universe state
            plot.owner = player_id
            
            # 2. Минтва NFT на blockchain
            result = self.blockchain.mint_plot_nft(player_id, plot_number, plot.zone)
            
            # 3. Свързва NFT с game asset
            plot.token_id = result['token_id']
            self.synced_assets['plots'].add(plot_number)
            
            print(f"✅ Парцел {plot_number} претендиран от {player_id}")
            return {'plot': plot, 'nft': result}
            
        except Exception as e:
            print(f"❌ Неуспешно претендиране: {str(e)}")
            raise
    
    def build_on_plot(self, player_id: str, plot_number: int, 
                     structure_type: StructureType) -> Dict:
        """Играч строи на парцел"""
        try:
            city = self.universe.get_city('Octavia Capital City')
            plot = next((p for p in city.plots if p.id == plot_number), None)
            
            if not plot:
                raise ValueError('Парцел не е намерен')
            if plot.owner != player_id:
                raise ValueError('Не сте собственик на парцела')
            if not plot.token_id:
                raise ValueError('Парцел не е минтнат като NFT')
            
            # 1. Проверява on-chain собственост
            is_owner = self.blockchain.check_ownership(player_id, plot.token_id)
            if not is_owner:
                raise ValueError('Blockchain собствеността не съвпада')
            
            # 2. Строи в играта
            city.develop_plot(plot_number, structure_type, player_id)
            
            # 3. Актуализира blockchain
            receipt = self.blockchain.build_structure_on_chain(plot.token_id, structure_type)
            
            self.synced_assets['structures'].add(f"{plot_number}_{structure_type.name}")
            
            print(f"✅ {structure_type.name} построен на парцел {plot_number}")
            return {'plot': plot, 'receipt': receipt}
            
        except Exception as e:
            print(f"❌ Строеж неуспешен: {str(e)}")
            raise
    
    def spawn_and_mint_npc(self, planet_id: int, player_id: str) -> Dict:
        """Създава NPC и минтва като NFT"""
        try:
            # 1. Създава в играта
            npc_id = len(self.universe.npcs) + 1
            npc = NPC(npc_id, planet_id, 50000 + npc_id)
            self.universe.npcs.append(npc)
            
            # 2. Минтва като NFT
            result = self.blockchain.mint_npc_nft(npc, player_id)
            
            # 3. Свързва
            npc.token_id = result['token_id']
            self.synced_assets['npcs'].add(npc_id)
            
            print(f"✅ NPC {npc.get_name()} създаден и минтнат")
            return {'npc': npc, 'nft': result}
            
        except Exception as e:
            print(f"❌ Създаване на NPC неуспешно: {str(e)}")
            raise
    
    def sync_npc_loyalty(self, npc_id: int, player_id: str):
        """Синхронизира лоялност на NPC към blockchain"""
        try:
            npc = self.universe.get_npc(npc_id)
            if not npc:
                raise ValueError('NPC не е намерен')
            if not npc.token_id:
                raise ValueError('NPC не е минтнат като NFT')
            
            current_loyalty = npc.loyalty.get(player_id, 0)
            previous_loyalty = npc._previous_loyalty.get(player_id, 0)
            
            if current_loyalty != previous_loyalty:
                self.blockchain.sync_npc_loyalty(
                    npc.token_id, player_id, current_loyalty, previous_loyalty
                )
                
                # Запазва предишна лоялност
                npc._previous_loyalty[player_id] = current_loyalty
            
        except Exception as e:
            print(f"❌ Синхронизация на лоялност неуспешна: {str(e)}")
            raise
    
    def npc_interaction(self, npc_id: int, player_id: str, 
                       interaction_type: str, quality: float = 1.0) -> Dict:
        """Взаимодействие с NPC"""
        try:
            npc = self.universe.get_npc(npc_id)
            if not npc:
                raise ValueError('NPC не е намерен')
            
            # 1. Обработва взаимодействието в играта
            new_loyalty = npc.interact_with_player(player_id, interaction_type, quality)
            
            # 2. Синхронизира към blockchain ако NPC е минтнат
            if npc.token_id and self.auto_sync:
                self.sync_npc_loyalty(npc_id, player_id)
            
            # 3. Проверява дали NPC се е присъединил към сферата на влияние
            if new_loyalty >= 100:
                print(f"🎉 {npc.get_name()} се присъедини към сферата на влияние на {player_id}!")
            
            return {'npc': npc, 'loyalty': new_loyalty}
            
        except Exception as e:
            print(f"❌ NPC взаимодействие неуспешно: {str(e)}")
            raise
    
    def extract_resources(self, planet_id: int, resource_type: str,
                         amount: int, extractor_address: str) -> Dict:
        """Извлича ресурси със синхронизация към blockchain"""
        try:
            planet = self.universe.get_planet(planet_id)
            if not planet:
                raise ValueError('Планета не е намерена')
            
            # 1. Извлича в играта
            extracted = planet.extract_resource(resource_type, amount)
            
            # 2. Синхронизира към blockchain
            receipt = self.blockchain.extract_and_sync_resource(
                planet_id, resource_type, amount, extractor_address
            )
            
            self.synced_assets['resources'].add(f"{planet_id}_{resource_type}_{len(self
