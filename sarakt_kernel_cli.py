#!/usr/bin/env python3
"""
SARAKT KERNEL - INTERACTIVE CLI (Python)
Административен команден интерфейс за управление на Sarakt Star System
"""

import cmd
import json
import sys
import os
from typing import Optional
from colorama import init, Fore, Style

# Импорт на модулите
from sarakt_universe_engine import SaraktUniverse, StructureType, NPCState
from sarakt_blockchain_integration import BlockchainConnector, SaraktBridge, get_config

# Инициализира colorama за цветен текст
init(autoreset=True)


class SaraktKernel(cmd.Cmd):
    """Интерактивен CLI за Sarakt Star System"""
    
    intro = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════╗
║         SARAKT KERNEL v1.0 - ADMIN CLI            ║
║    Sarakt Star System Management Interface         ║
╚════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}Dynasty Dulo Descendant Protocol Active{Style.RESET_ALL}
Въведете 'help' за налични команди
    """
    
    prompt = f'{Fore.GREEN}sarakt> {Style.RESET_ALL}'
    
    def __init__(self):
        super().__init__()
        self.universe: Optional[SaraktUniverse] = None
        self.blockchain: Optional[BlockchainConnector] = None
        self.bridge: Optional[SaraktBridge] = None
        self.history = []
    
    # ============================================
    # СИСТЕМНИ КОМАНДИ
    # ============================================
    
    def do_init(self, arg):
        """Инициализира Sarakt вселената"""
        print(f"{Fore.CYAN}🚀 Инициализиране на Sarakt Star System...{Style.RESET_ALL}\n")
        self.universe = SaraktUniverse()
        print(f"{Fore.GREEN}✅ Вселена инициализирана успешно{Style.RESET_ALL}\n")
    
    def do_config(self, arg):
        """Конфигурира blockchain връзка: config <rpc_url> [contract_address]"""
        args = arg.split()
        if len(args) < 1:
            print('Употреба: config <rpc_url> [contract_address]')
            return
        
        config = get_config()
        config['rpc_url'] = args[0]
        if len(args) > 1:
            config['contract_address'] = args[1]
        
        try:
            print(f"{Fore.CYAN}⚙️  Конфигуриране на blockchain връзка...{Style.RESET_ALL}")
            self.blockchain = BlockchainConnector(config)
            self.bridge = SaraktBridge(self.universe, self.blockchain)
            print(f"{Fore.GREEN}✅ Blockchain конфигуриран успешно{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Конфигурацията неуспешна: {e}{Style.RESET_ALL}")
    
    def do_status(self, arg):
        """Показва статус на системата"""
        if not self.universe:
            print(f"{Fore.RED}❌ Вселената не е инициализирана. Изпълнете 'init' първо.{Style.RESET_ALL}")
            return
        
        status = self.universe.get_universe_status()
        
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════╗")
        print(f"║              СТАТУС НА СИСТЕМА SARAKT              ║")
        print(f"╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"Цикъл: {status['cycle']}")
        print(f"Общо планети: {status['total_planets']}")
        print(f"Обитаеми планети: {status['habitable_planets']}")
        print(f"Градове: {status['total_cities']}")
        print(f"Общо NPCs: {status['total_npcs']}")
        print(f"Зрели NPCs: {status['mature_npcs']}")
        print(f"Лоялни NPCs: {status['loyal_npcs']}")
        
        if self.bridge:
            print(f"\n{Fore.YELLOW}Blockchain синхронизация:{Style.RESET_ALL}")
            sync_status = self.bridge.get_sync_status()
            print(f"  Парцели: {sync_status['plots']}")
            print(f"  NPCs: {sync_status['npcs']}")
            print(f"  Структури: {sync_status['structures']}")
            print(f"  Ресурси: {sync_status['resources']}")
            print(f"  Авто-синх: {'✓' if sync_status['auto_sync'] else '✗'}")
        print()
    
    def do_clear(self, arg):
        """Изчиства екрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.intro)
    
    def do_exit(self, arg):
        """Излиза от Sarakt Kernel"""
        print(f"\n{Fore.YELLOW}👋 Изключване на Sarakt Kernel...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Dynasty Dulo Protocol прекратен.{Style.RESET_ALL}\n")
        return True
    
    # Синоним за exit
    do_quit = do_exit
    
    # ============================================
    # КОМАНДИ ЗА ПЛАНЕТИ
    # ============================================
    
    def do_planet_list(self, arg):
        """Показва списък с всички планети"""
        if not self.universe:
            print(f"{Fore.RED}❌ Вселената не е инициализирана.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════╗")
        print(f"║                   РЕГИСТЪР ПЛАНЕТИ                 ║")
        print(f"╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        for planet in self.universe.planets:
            status_icon = '🌍 Обитаема' if planet.is_habitable else '⛏️  Минна'
            print(f"[{planet.id}] {planet.name:<25} {status_icon}")
        print()
    
    def do_planet_info(self, arg):
        """Показва информация за планета: planet_info <planetId|name>"""
        if not arg:
            print('Употреба: planet_info <planetId|name>')
            return
        
        try:
            planet_id = int(arg)
            planet = self.universe.get_planet(planet_id)
        except ValueError:
            planet = self.universe.get_planet(arg)
        
        if not planet:
            print(f"{Fore.RED}❌ Планета не е намерена{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════╗")
        print(f"║  ПЛАНЕТА: {planet.name:<43}║")
        print(f"╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print('Свойства:')
        print(f"  ID: {planet.id}")
        print(f"  Тип: {planet.type.value}")
        print(f"  Обитаема: {'Да' if planet.is_habitable else 'Не'}")
        print(f"  Seed: {planet.seed}")
        print(f"  Радиус: {planet.properties['radius']} km")
        print(f"  Гравитация: {planet.properties['gravity']:.2f}g")
        print(f"  Атмосфера: {planet.properties['atmosphere']}")
        print(f"  Температура: {planet.properties['temperature']}°C")
        print(f"  Водно покритие: {planet.properties['water_coverage'] * 100:.1f}%")
        
        print(f"\nБиоми: {len(planet.biomes)}")
        for biome in planet.biomes[:5]:
            print(f"  - {biome.type} ({biome.coverage * 100:.0f}% покритие)")
        
        print(f"\nРегиони: {len(planet.regions)}")
        print(f"Опасни зони: {len(planet.danger_zones)}")
        print()
    
    def do_planet_resources(self, arg):
        """Показва ресурси на планета: planet_resources <planetId>"""
        if not arg:
            print('Употреба: planet_resources <planetId>')
            return
        
        try:
            planet_id = int(arg)
            planet = self.universe.get_planet(planet_id)
        except ValueError:
            print(f"{Fore.RED}❌ Невалиден ID на планета{Style.RESET_ALL}")
            return
        
        if not planet:
            print(f"{Fore.RED}❌ Планета не е намерена{Style.RESET_ALL}")
            return
        
        resources = planet.get_resource_summary()
        
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════╗")
        print(f"║  РЕСУРСИ: {planet.name:<38}║")
        print(f"╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        for resource, amount in resources[:15]:
            print(f"  {resource:<20} {amount:>15,}")
        print()
    
    def do_planet_extract(self, arg):
        """Извлича ресурс: planet_extract <planetId> <resource> <amount>"""
        args = arg.split()
        if len(args) < 3:
            print('Употреба: planet_extract <planetId> <resource> <amount>')
            return
        
        try:
            planet_id = int(args[0])
            resource = args[1]
            amount = int(args[2])
            
            if self.bridge:
                result = self.bridge.extract_resources(
                    planet_id, resource, amount, self.blockchain.address
                )
                print(f"{Fore.GREEN}✅ Извлечени {amount} {resource} от планета {planet_id}{Style.RESET_ALL}")
                print(f"TX Hash: {result['receipt']['tx_hash']}")
            else:
                planet = self.universe.get_planet(planet_id)
                planet.extract_resource(resource, amount)
                print(f"{Fore.GREEN}✅ Извлечени {amount} {resource} (само off-chain){Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Извличането неуспешно: {e}{Style.RESET_ALL}")
    
    # ============================================
    # КОМАНДИ ЗА ГРАДОВЕ
    # ============================================
    
    def do_city_list(self, arg):
        """Показва списък с градове"""
        if not self.universe:
            print(f"{Fore.RED}❌ Вселената не е инициализирана.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════╗")
        print(f"║                    РЕГИСТЪР ГРАДОВЕ                ║")
        print(f"╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        for city in self.universe.cities:
            stats = city.get_city_stats()
            print(f"[{city.id}] {city.name}")
            print(f"     Парцели: {stats['developed_plots']}/{stats['total_plots']} ({stats['development_percent']}%)")
            print(f"     Население: {stats['population']:,}")
            print()
    
    def do_city_info(self, arg):
        """Показва информация за град: city_info <cityId>"""
        if not arg:
            print('Употреба: city_info <cityId>')
            return
        
        try:
            city_id = int(arg)
            city = self.universe.cities[city_id - 1]
        except (ValueError, IndexError):
            print(f"{Fore.RED}❌ Град не е намерен{Style.RESET_ALL}")
            return
        
        stats = city.get_city_stats()
        
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════╗")
        print(f"║  ГРАД: {stats['name']:<45}║")
        print(f"╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"Развитие: {stats['developed_plots']}/{stats['total_plots']} парцела ({stats['development_percent']}%)")
        print(f"Население: {stats['population']:,}")
        print(f"GDP: {stats['gdp']:,} xBGL")
        print(f"Заетост: {stats['employment']:,}")
        print(f"Безработица: {stats['unemployment']:,}")
        
        print('\nИнфраструктура:')
        for infra in stats['infrastructure'][:10]:
            print(f"  {infra['name']:<20} {infra['status']:<15} {infra['coverage']}")
        print()
    
    def do_city_claim(self, arg):
        """Претендира парцел: city_claim <cityId> <plotNumber> <playerAddress>"""
        args = arg.split()
        if len(args) < 3:
            print('Употреба: city_claim <cityId> <plotNumber> <playerAddress>')
            return
        
        try:
            city_id = int(args[0])
            plot_number = int(args[1])
            player_address = args[2]
            
            if self.bridge:
                result = self.bridge.claim_plot(player_address, plot_number)
                print(f"{Fore.GREEN}✅ Парцел {plot_number} претендиран от {player_address}{Style.RESET_ALL}")
                print(f"Token ID: {result['nft']['token_id']}")
                print(f"TX Hash: {result['nft']['tx_hash']}")
            else:
                print(f"{Fore.RED}❌ Blockchain bridge не е конфигуриран. Използвайте 'config' първо.{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Претендирането неуспешно: {e}{Style.RESET_ALL}")
    
    def do_city_build(self, arg):
        """Строи структура: city_build <plotNumber> <structureType>"""
        args = arg.split()
        if len(args) < 2:
            print('Употреба: city_build <plotNumber> <structureType>')
            print('Типове структури: HUT, WOODEN_HOUSE, STONE_HOUSE, WORKSHOP, COMMERCIAL')
            return
        
        try:
            plot_number = int(args[0])
            structure_name = args[1].upper()
            structure_type = StructureType[structure_name]
            
            if self.bridge:
                # Взима собственика на парцела
                city = self.universe.get_city('Octavia Capital City')
                plot = next((p for p in city.plots if p.id == plot_number), None)
                
                if not plot or not plot.owner:
                    print(f"{Fore.RED}❌ Парцел не е намерен или не е притежаван{Style.RESET_ALL}")
                    return
                
                result = self.bridge.build_on_plot(plot.owner, plot_number, structure_type)
                print(f"{Fore.GREEN}✅ {structure_name} построен на парцел {plot_number}{Style.RESET_ALL}")
                print(f"TX Hash: {result['receipt']['tx_hash']}")
            else:
                print(f"{Fore.RED}❌ Blockchain bridge не е конфигуриран.{Style.RESET_ALL}")
        
        except KeyError:
            print(f"{Fore.RED}❌ Невалиден тип структура{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Строеж неуспешен: {e}{Style.RESET_ALL}")
    
    # ============================================
    # КОМАНДИ ЗА NPCs
    # ============================================
    
    def do_npc_list(self, arg):
        """Показва списък с NPCs: npc_list [filter]"""
        if not self.universe:
            print(f"{Fore.RED}❌ Вселената не е инициализирана.{Style.RESET_ALL}")
            return
        
        filter_type = arg.strip() if arg else 'all'
        npcs = self.universe.npcs
        
        if filter_type == 'mature':
            npcs = [npc for npc in npcs if npc.state == NPCState.MATURE]
        elif filter_type == 'loyal':
            npcs = [npc for npc in npcs if npc.state == NPCState.LOYAL]
        elif filter_type == 'developing':
            npcs = [npc for npc in npcs if npc.state == NPCState.DEVELOPING]
        
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════╗")
        print(f"║  NPC РЕГИСТЪР ({filter_type})".ljust(52) + f"║")
        print(f"╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        for npc in npcs[:20]:
            status = f"Възраст: {npc.age}, Състояние: {npc.state.value}"
            print(f"[{npc.id}] {npc.get_name():<30} {status}")
        
        if len(npcs) > 20:
            print(f"\n... и още {len(npcs) - 20}\n")
        else:
            print()
    
    def do_npc_info(self, arg):
        """Показва информация за NPC: npc_info <npcId>"""
        if not arg:
            print('Употреба: npc_info <npcId>')
            return
        
        try:
            npc_id = int(arg)
            npc = self.universe.get_npc(npc_id)
        except ValueError:
            print(f"{Fore.RED}❌ Невалиден NPC ID{Style.RESET_ALL}")
            return
        
        if not npc:
            print(f"{Fore.RED}❌ NPC не е намерен{Style.RESET_ALL}")
            return
        
        status = npc.get_status()
        
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════════════╗")
        print(f"║  NPC: {status['name']:<44}║")
        print(f"╚════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")
        
        print(f"ID: {status['id']}")
        print(f"Възраст: {status['age']}")
        print(f"Състояние: {status['state']}")
        print(f"Наследство: {status['heritage']}, Поколение: {status['generation']}")
        
        print('\nАтрибути:')
        for attr, val in status['attributes'].items():
            print(f"  {attr:<15} {val}/10")
        
        if status['personality']:
            print('\nЧерти на личността:')
            for trait, val in status['personality'].items():
                bar = '█' * int(val * 10)
                print(f"  {trait:<20} {bar} {val * 100:.0f}%")
        
        if status['top_skills']:
            print('\nТоп умения:')
            for skill, level in status['top_skills']:
                print(f"  {skill:<20} {level}")
        
        if status['loyalties']:
            print('\nЛоялност:')
            for player, loyalty in status['loyalties'].items():
                print(f"  {player[:20]}... {loyalty:.1f}/100")
        print()
    
    def do_npc_spawn(self, arg):
        """Създава NPC: npc_spawn <planetId> <playerAddress>"""
        args = arg.split()
        if len(args) < 2:
            print('Употреба: npc_spawn <planetId> <playerAddress>')
            return
        
        try:
            planet_id = int(args[0])
            player_address = args[1]
            
            if self.bridge:
                result = self.bridge.spawn_and_mint_npc(planet_id, player_address)
                print(f"{Fore.GREEN}✅ NPC създаден: {result['npc'].get_name()}{Style.RESET_ALL}")
                print(f"Token ID: {result['nft']['token_id']}")
                print(f"TX Hash: {result['nft']['tx_hash']}")
            else:
                from sarakt_universe_engine import NPC
                npc_id = len(self.universe.npcs) + 1
                npc = NPC(npc_id, planet_id, 50000 + npc_id)
                self.universe.npcs.append(npc)
                print(f"{Fore.GREEN}✅ NPC създаден: {npc.get_name()} (само off-chain){Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Създаването неуспешно: {e}{Style.RESET_ALL}")
    
    def do_npc_interact(self, arg):
        """Взаимодействие с NPC: npc_interact <npcId> <playerId> <type> [quality]"""
        args = arg.split()
        if len(args) < 3:
            print('Употреба: npc_interact <npcId> <playerId> <type> [quality]')
            print('Типове: positive_trade, quest_completion, gift, rescue, employment, betrayal, harm, neglect')
            return
        
        try:
            npc_id = int(args[0])
            player_id = args[1]
            interaction_type = args[2]
            quality = float(args[3]) if len(args) > 3 else 1.0
            
            if self.bridge:
                result = self.bridge.npc_interaction(npc_id, player_id, interaction_type, quality)
                print(f"{Fore.GREEN}✅ Взаимодействие обработено. Нова лоялност: {result['loyalty']:.1f}/100{Style.RESET_ALL}")
            else:
                npc = self.universe.get_npc(npc_id)
                loyalty = npc.interact_with_player(player_id, interaction_type, quality)
                print(f"{Fore.GREEN}✅ Взаимодействие обработено. Нова лоялност: {loyalty:.1f}/100{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}❌ Взаимодействието неуспешно: {e}{Style.RESET_ALL}")
    
    # ============================================
    # СИМУЛАЦИОННИ КОМАНДИ
    # ============================================
    
    def do_sim_cycle(self, arg):
        """Симулира цикли: sim_cycle [cycles]"""
        cycles = int(arg) if arg else 1
        
        print(f"\n{Fore.CYAN}⚙️  Симулиране на {cycles} цикъл(а)...{Style.RESET_ALL}\n")
        
        if self.bridge:
            self.bridge.simulate
