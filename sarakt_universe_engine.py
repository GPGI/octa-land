"""
SARAKT STAR SYSTEM - UNIVERSE ENGINE (Python)
Процедурна генерация и симулация на вселената
"""

import random
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# ============================================
# ENUMS И КОНСТАНТИ
# ============================================

class PlanetType(Enum):
    HABITABLE_PRIMARY = "habitable_primary"
    HABITABLE_BIOTECH = "habitable_biotech"
    MINING_STANDARD = "mining_standard"
    UNEXPLORED = "unexplored"


class AssetType(Enum):
    PLANET = 0
    LAND_PLOT = 1
    STRUCTURE = 2
    NPC = 3
    RESOURCE = 4
    BUSINESS = 5
    VEHICLE = 6
    BOND = 7
    FACTION_TOKEN = 8
    ARTIFACT = 9


class StructureType(Enum):
    EMPTY_PLOT = 0
    HUT = 1  # 15% net value
    WOODEN_HOUSE = 2  # 35% net value
    STONE_HOUSE = 3  # 60% net value
    WORKSHOP = 4
    COMMERCIAL = 5
    INFRASTRUCTURE = 6


class NPCState(Enum):
    CHILD = "child"
    DEVELOPING = "developing"
    MATURE = "mature"
    LOYAL = "loyal"


class Rarity(Enum):
    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    EPIC = 3
    LEGENDARY = 4


# ============================================
# ПРОЦЕДУРЕН ГЕНЕРАТОР
# ============================================

class ProceduralGenerator:
    """Генератор на случайни числа със seed за детерминистична генерация"""
    
    def __init__(self, seed: int):
        self.seed = seed
        self.rng = random.Random(seed)
    
    def random(self, min_val: float = 0, max_val: float = 1) -> float:
        """Връща случайно число между min_val и max_val"""
        return min_val + self.rng.random() * (max_val - min_val)
    
    def randint(self, min_val: int, max_val: int) -> int:
        """Връща случайно цяло число"""
        return self.rng.randint(min_val, max_val)
    
    def choice(self, items: list):
        """Избира случаен елемент от списък"""
        return self.rng.choice(items)
    
    def weighted_choice(self, options: List[Tuple[any, float]]):
        """Избира елемент въз основа на тежести"""
        total = sum(weight for _, weight in options)
        r = self.random(0, total)
        
        for value, weight in options:
            if r < weight:
                return value
            r -= weight
        
        return options[0][0]


# ============================================
# ПЛАНЕТА
# ============================================

@dataclass
class BiomeData:
    id: int
    type: str
    coverage: float
    avg_temperature: int
    rainfall: int
    elevation: int
    danger_level: int


@dataclass
class RegionData:
    id: int
    name: str
    biome_type: str
    coordinates: Dict[str, float]
    size: int
    population: int
    development: float
    points_of_interest: List[Dict]


class Planet:
    """Клас за планета в системата Sarakt"""
    
    def __init__(self, planet_id: int, name: str, seed: int, 
                 planet_type: PlanetType, is_habitable: bool):
        self.id = planet_id
        self.name = name
        self.seed = seed
        self.type = planet_type
        self.is_habitable = is_habitable
        self.generator = ProceduralGenerator(seed)
        
        self.properties = self._generate_properties()
        self.biomes = self._generate_biomes()
        self.resources = self._generate_resources()
        self.regions = self._generate_regions()
        self.danger_zones = self._generate_danger_zones()
    
    def _generate_properties(self) -> Dict:
        """Генерира физични свойства на планетата"""
        gen = self.generator
        
        return {
            'radius': gen.randint(3000, 12000),  # km
            'gravity': gen.random(0.3, 2.5),  # Earth = 1.0
            'atmosphere': self._get_atmosphere_type(),
            'temperature': gen.randint(-150, 50),  # Celsius
            'day_length': gen.randint(18, 36),  # часове
            'year_length': gen.randint(200, 800),  # дни
            'moons': gen.randint(0, 3),
            'water_coverage': gen.random(0.2, 0.7) if self.is_habitable else gen.random(0, 0.1),
            'axial_tilt': gen.randint(0, 45)
        }
    
    def _get_atmosphere_type(self) -> str:
        if self.type == PlanetType.HABITABLE_PRIMARY:
            return 'breathable'
        elif self.type == PlanetType.HABITABLE_BIOTECH:
            return 'toxic_breathable'
        else:
            return 'none'
    
    def _generate_biomes(self) -> List[BiomeData]:
        """Генерира биоми на планетата"""
        gen = self.generator
        biome_count = gen.randint(3, 8)
        biomes = []
        
        biome_types = (
            ['forest', 'plains', 'mountains', 'desert', 'tundra', 'swamp', 'jungle', 'volcanic']
            if self.is_habitable else
            ['barren', 'frozen', 'volcanic', 'crystalline', 'metallic', 'radioactive']
        )
        
        for i in range(biome_count):
            biomes.append(BiomeData(
                id=i,
                type=gen.choice(biome_types),
                coverage=gen.random(0.05, 0.3),
                avg_temperature=gen.randint(-50, 50),
                rainfall=gen.randint(0, 2000),
                elevation=gen.randint(-500, 8000),
                danger_level=gen.randint(1, 10)
            ))
        
        return biomes
    
    def _generate_resources(self) -> Dict[str, int]:
        """Генерира ресурси на планетата"""
        gen = self.generator
        resources = {}
        
        resource_types = {
            'common': ['iron', 'copper', 'stone', 'wood', 'water'],
            'uncommon': ['silver', 'gold', 'titanium', 'uranium', 'crystals'],
            'rare': ['platinum', 'rare_earths', 'exotic_matter', 'alien_artifacts'],
            'legendary': ['zero_point_energy', 'antimatter', 'dynasty_dulo_relics']
        }
        
        # Всички планети имат основни ресурси
        for resource in resource_types['common']:
            resources[resource] = gen.randint(10000, 100000)
        
        # Обитаеми планети - повече разнообразие
        if self.is_habitable:
            for resource in resource_types['uncommon']:
                if gen.random() > 0.3:
                    resources[resource] = gen.randint(1000, 50000)
        else:
            # Минни планети - МНОГО минерали
            for resource in resource_types['uncommon']:
                resources[resource] = gen.randint(50000, 500000)
        
        # Редки ресурси
        for resource in resource_types['rare']:
            if gen.random() > 0.7:
                resources[resource] = gen.randint(100, 10000)
        
        # Легендарни ресурси (много редки)
        if gen.random() > 0.95:
            legendary = gen.choice(resource_types['legendary'])
            resources[legendary] = gen.randint(1, 1000)
        
        # Специално: Zythera нанофибърни ресурси
        if self.name == 'Zythera':
            resources['nanofiber_web'] = gen.randint(100000, 500000)
            resources['biotech_samples'] = gen.randint(50000, 200000)
            resources['chaos_crystals'] = gen.randint(10000, 50000)
        
        return resources
    
    def _generate_regions(self) -> List[RegionData]:
        """Генерира региони на планетата"""
        gen = self.generator
        region_count = 5 + int(gen.random() * 10)
        regions = []
        
        for i in range(region_count):
            biome = gen.choice(self.biomes)
            
            regions.append(RegionData(
                id=i,
                name=self._generate_region_name(i),
                biome_type=biome.type,
                coordinates={'lat': gen.random(-90, 90), 'lon': gen.random(-180, 180)},
                size=gen.randint(100, 10000),
                population=gen.randint(0, 50000) if self.is_habitable else 0,
                development=gen.random(0, 1) if self.is_habitable else 0,
                points_of_interest=self._generate_pois(gen.randint(1, 5))
            ))
        
        return regions
    
    def _generate_region_name(self, region_id: int) -> str:
        """Генерира име на регион"""
        prefixes = ['North', 'South', 'East', 'West', 'Central', 'Upper', 'Lower', 'New']
        suffixes = ['Highlands', 'Valley', 'Plains', 'Reach', 'Territory', 'Expanse', 'Zone']
        
        if self.generator.random() > 0.5:
            return f"{self.generator.choice(prefixes)} {self.generator.choice(suffixes)}"
        return f"Region {region_id + 1}"
    
    def _generate_pois(self, count: int) -> List[Dict]:
        """Генерира точки от интерес"""
        pois = []
        types = ['cave', 'ruins', 'crash_site', 'resource_deposit', 'anomaly', 'outpost']
        
        for i in range(count):
            pois.append({
                'type': self.generator.choice(types),
                'name': f"POI-{self.id}-{i}",
                'discovered': False,
                'danger_level': self.generator.randint(1, 10)
            })
        
        return pois
    
    def _generate_danger_zones(self) -> List[Dict]:
        """Генерира опасни зони"""
        gen = self.generator
        zone_count = gen.randint(2, 8)
        zones = []
        
        hazards = ['radiation', 'toxic_gas', 'extreme_temperature', 'hostile_creatures',
                   'unstable_terrain', 'magnetic_anomaly', 'nanofiber_infection']
        
        for i in range(zone_count):
            zones.append({
                'id': i,
                'hazard': gen.choice(hazards),
                'severity': gen.randint(1, 10),
                'radius': gen.randint(5, 50),
                'is_active': gen.random() > 0.3
            })
        
        return zones
    
    def extract_resource(self, resource_type: str, amount: int) -> int:
        """Извлича ресурс от планетата"""
        if resource_type not in self.resources:
            raise ValueError(f"Resource {resource_type} not available on {self.name}")
        
        if self.resources[resource_type] < amount:
            raise ValueError(f"Insufficient {resource_type}. Available: {self.resources[resource_type]}")
        
        self.resources[resource_type] -= amount
        return amount
    
    def get_resource_summary(self) -> List[Tuple[str, int]]:
        """Връща резюме на ресурсите"""
        return sorted(
            [(res, amt) for res, amt in self.resources.items() if amt > 0],
            key=lambda x: x[1],
            reverse=True
        )


# ============================================
# NPC СИСТЕМА
# ============================================

class NPC:
    """NPC с Dynasty Dulo наследство и развиваща се личност"""
    
    def __init__(self, npc_id: int, planet_id: int, seed: int):
        self.id = npc_id
        self.planet_id = planet_id
        self.seed = seed
        self.generator = ProceduralGenerator(seed)
        
        # Dynasty Dulo наследство
        self.heritage = 'Dynasty_Dulo'
        self.generation = self.generator.randint(1, 10)
        
        # Стартиране като дете без личност
        self.age = 0
        self.state = NPCState.CHILD
        self.personality = None
        self.skills = {}
        self.loyalty = {}
        self.relationships = {}
        self.memories = []
        
        # Физически атрибути
        self.attributes = self._generate_attributes()
        self.token_id = None
        self._previous_loyalty = {}
    
    def _generate_attributes(self) -> Dict[str, int]:
        """Генерира физически атрибути"""
        gen = self.generator
        return {
            'strength': gen.randint(1, 10),
            'intelligence': gen.randint(1, 10),
            'charisma': gen.randint(1, 10),
            'endurance': gen.randint(1, 10),
            'agility': gen.randint(1, 10)
        }
    
    def age_cycle(self, cycles: int = 1):
        """Остарява NPC и развива личност"""
        self.age += cycles
        
        # Деца стават "развиващи се" на 5 години
        if self.age >= 5 and self.state == NPCState.CHILD:
            self.state = NPCState.DEVELOPING
            self._develop_personality()
        
        # Развиващите се стават "зрели" на 18 години
        if self.age >= 18 and self.state == NPCState.DEVELOPING:
            self.state = NPCState.MATURE
            self._refine_personality()
        
        # Развитие на умения
        self._develop_skills()
    
    def _develop_personality(self):
        """Развива личност (Big Five + Sarakt специфични черти)"""
        gen = self.generator
        
        self.personality = {
            'openness': gen.random(0, 1),
            'conscientiousness': gen.random(0, 1),
            'extraversion': gen.random(0, 1),
            'agreeableness': gen.random(0, 1),
            'neuroticism': gen.random(0, 1),
            
            # Sarakt специфични черти
            'rebelliousness': gen.random(0, 1),  # Dynasty Dulo наследство
            'adaptability': gen.random(0, 1),
            'loyalty_tendency': gen.random(0, 1)
        }
    
    def _refine_personality(self):
        """Изчиства личността с възрастта"""
        for trait in self.personality:
            variance = self.generator.random(-0.1, 0.1)
            self.personality[trait] = max(0, min(1, self.personality[trait] + variance))
    
    def _develop_skills(self):
        """Развива умения"""
        available_skills = [
            'woodcutting', 'hunting', 'farming', 'water_gathering',
            'mining', 'crafting', 'combat', 'trading', 'construction',
            'engineering', 'biotech', 'leadership', 'stealth'
        ]
        
        if self.age >= 5:
            for skill in available_skills:
                if skill not in self.skills:
                    self.skills[skill] = 0
                
                growth_rate = self._get_skill_growth_rate(skill)
                self.skills[skill] = min(100, self.skills[skill] + growth_rate)
    
    def _get_skill_growth_rate(self, skill: str) -> float:
        """Изчислява скоростта на развитие на умение"""
        if not self.personality:
            return 0.1
        
        base_rate = 0.1
        modifier = 1.0
        
        if skill == 'leadership':
            modifier += self.attributes['charisma'] / 10
        elif skill == 'engineering' and self.personality['openness']:
            modifier += self.personality['openness']
        elif skill in ['mining', 'woodcutting']:
            modifier += self.attributes['strength'] / 20
        
        return base_rate * modifier
    
    def interact_with_player(self, player_id: str, interaction_type: str, quality: float = 1.0) -> float:
        """Взаимодействие с играч - променя лоялност"""
        if player_id not in self.loyalty:
            self.loyalty[player_id] = 0
        
        interaction_effects = {
            'positive_trade': 2,
            'quest_completion': 5,
            'gift': 3,
            'rescue': 10,
            'employment': 1,
            'betrayal': -20,
            'harm': -15,
            'neglect': -1
        }
        
        loyalty_change = interaction_effects.get(interaction_type, 0) * quality
        
        # Личността влияе на промяната в лоялността
        if self.personality and self.personality['loyalty_tendency'] > 0.7:
            loyalty_change *= 1.5
        elif self.personality and self.personality['loyalty_tendency'] < 0.3:
            loyalty_change *= 0.5
        
        self.loyalty[player_id] = max(0, min(100, self.loyalty[player_id] + loyalty_change))
        
        # При 100% лоялност, NPC се присъединява към сферата на влияние
        if self.loyalty[player_id] >= 100 and self.state != NPCState.LOYAL:
            self.state = NPCState.LOYAL
            self._join_sphere(player_id)
        
        # Записва паметта
        self.memories.append({
            'timestamp': datetime.now().isoformat(),
            'player_id': player_id,
            'interaction_type': interaction_type,
            'loyalty_change': loyalty_change,
            'current_loyalty': self.loyalty[player_id]
        })
        
        return self.loyalty[player_id]
    
    def _join_sphere(self, player_id: str):
        """NPC се присъединява към сферата на влияние на играч"""
        print(f"🎉 NPC {self.id} ({self.get_name()}) се присъедини към сферата на влияние на {player_id}!")
    
    def get_name(self) -> str:
        """Генерира Dynasty Dulo име"""
        first_names = ['Alexei', 'Boris', 'Dimitri', 'Elena', 'Fyodor', 'Galina',
                      'Ivan', 'Katerina', 'Leonid', 'Marina', 'Nikolai', 'Olga']
        last_names = ['Dulov', 'Petrov', 'Ivanov', 'Volkov', 'Sokolov', 'Kozlov']
        
        first = self.generator.choice(first_names)
        last = self.generator.choice(last_names)
        
        return f"{first} {last}"
    
    def get_status(self) -> Dict:
        """Връща статус на NPC"""
        top_skills = sorted(self.skills.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'id': self.id,
            'name': self.get_name(),
            'age': self.age,
            'state': self.state.value,
            'heritage': self.heritage,
            'generation': self.generation,
            'attributes': self.attributes,
            'personality': self.personality,
            'top_skills': [(skill, f"{level:.1f}") for skill, level in top_skills],
            'loyalties': self.loyalty
        }
    
    def get_top_skills(self, count: int = 5) -> List[Tuple[str, str]]:
        """Връща топ умения"""
        top = sorted(self.skills.items(), key=lambda x: x[1], reverse=True)[:count]
        return [(skill, f"{level:.1f}") for skill, level in top]


# ============================================
# ГРАД (OCTAVIA CAPITAL CITY)
# ============================================

@dataclass
class Plot:
    id: int
    zone: str
    owner: Optional[str] = None
    structure_type: StructureType = StructureType.EMPTY_PLOT
    net_value: int = 0
    developed: bool = False
    token_id: Optional[int] = None


class City:
    """Клас за град в системата Sarakt"""
    
    def __init__(self, city_id: int, name: str, planet_id: int, total_plots: int):
        self.id = city_id
        self.name = name
        self.planet_id = planet_id
        self.total_plots = total_plots
        
        self.plots = self._initialize_plots()
        self.infrastructure = self._initialize_infrastructure()
        self.economy = self._initialize_economy()
        self.population = 0
        self.npcs = []
    
    def _initialize_plots(self) -> List[Plot]:
        """Инициализира парцели - 50% жилищни, 30% бизнес, 20% индустриални"""
        plots = []
        
        residential = int(self.total_plots * 0.5)
        commercial = int(self.total_plots * 0.3)
        industrial = self.total_plots - residential - commercial
        
        for i in range(1, self.total_plots + 1):
            if i <= residential:
                zone = 'residential'
            elif i <= residential + commercial:
                zone = 'commercial'
            else:
                zone = 'industrial'
            
            plots.append(Plot(id=i, zone=zone))
        
        return plots
    
    def _initialize_infrastructure(self) -> Dict:
        """Инициализира инфраструктура"""
        return {
            'sewage_system': {'level': 0, 'coverage': 0, 'cost': 50000},
            'water_system': {'level': 0, 'coverage': 0, 'cost': 75000},
            'harbor': {'exists': False, 'capacity': 0, 'cost': 200000},
            'elevator': {'exists': False, 'capacity': 0, 'cost': 150000},
            'roads': {'level': 0, 'coverage': 0, 'cost': 30000},
            'power_grid': {'level': 0, 'coverage': 0, 'cost': 100000},
            'school': {'exists': False, 'capacity': 0, 'cost': 80000},
            'university': {'exists': False, 'capacity': 0, 'cost': 300000},
            'hospital': {'exists': False, 'capacity': 0, 'cost': 250000}
        }
    
    def _initialize_economy(self) -> Dict:
        """Инициализира икономика"""
        return {
            'gdp': 0,
            'tax_revenue': 0,
            'employment': 0,
            'unemployment': 0,
            'average_income': 0,
            'industries': {
                'woodcutting': {'workers': 0, 'output': 0},
                'hunting': {'workers': 0, 'output': 0},
                'farming': {'workers': 0, 'output': 0},
                'water_gathering': {'workers': 0, 'output': 0},
                'workshops': {'workers': 0, 'output': 0},
                'trading': {'workers': 0, 'output': 0}
            }
        }
    
    def develop_plot(self, plot_id: int, structure_type: StructureType, owner: str) -> Plot:
        """Развива парцел"""
        plot = next((p for p in self.plots if p.id == plot_id), None)
        
        if not plot:
            raise ValueError('Plot not found')
        if plot.developed:
            raise ValueError('Plot already developed')
        
        plot.structure_type = structure_type
        plot.owner = owner
        plot.developed = True
        
        # Задава нетна стойност според типа структура (от whitepaper)
        net_values = {
            StructureType.HUT: 15,
            StructureType.WOODEN_HOUSE: 35,
            StructureType.STONE_HOUSE: 60,
            StructureType.WORKSHOP: 40,
            StructureType.COMMERCIAL: 50,
            StructureType.INFRASTRUCTURE: 30
        }
        
        plot.net_value = net_values.get(structure_type, 0)
        
        self._update_city_stats()
        return plot
    
    def build_infrastructure(self, infra_type: str):
        """Строи инфраструктура"""
        if infra_type not in self.infrastructure:
            raise ValueError('Invalid infrastructure type')
        
        infra = self.infrastructure[infra_type]
        
        if 'level' in infra:
            infra['level'] += 1
            infra['coverage'] = min(1.0, infra['coverage'] + 0.2)
        else:
            infra['exists'] = True
            infra['capacity'] = 1000
        
        self._update_city_stats()
    
    def _update_city_stats(self):
        """Актуализира статистиките на града"""
        developed = sum(1 for p in self.plots if p.developed)
        
        # Актуализира населението
        housing = [p for p in self.plots if p.structure_type in [
            StructureType.HUT, StructureType.WOODEN_HOUSE, StructureType.STONE_HOUSE
        ]]
        self.population = len(housing) * 4  # Средно 4 души на жилище
        
        # Изчислява GDP
        self.economy['gdp'] = sum(p.net_value * 1000 for p in self.plots if p.developed)
        
        # Изчислява заетост
        workplaces = [p for p in self.plots if p.structure_type in [
            StructureType.WORKSHOP, StructureType.COMMERCIAL
        ]]
        self.economy['employment'] = min(self.population * 0.6, len(workplaces) * 10)
        self.economy['unemployment'] = max(0, (self.population * 0.6) - self.economy['employment'])
    
    def get_city_stats(self) -> Dict:
        """Връща статистики на града"""
        developed = sum(1 for p in self.plots if p.developed)
        
        return {
            'name': self.name,
            'total_plots': self.total_plots,
            'developed_plots': developed,
            'development_percent': f"{(developed / self.total_plots) * 100:.1f}",
            'population': self.population,
            'gdp': self.economy['gdp'],
            'employment': self.economy['employment'],
            'unemployment': self.economy['unemployment'],
            'infrastructure': self._get_infrastructure_summary()
        }
    
    def _get_infrastructure_summary(self) -> List[Dict]:
        """Връща резюме на инфраструктурата"""
        summary = []
        for name, data in self.infrastructure.items():
            status = 'built' if data.get('exists') else f"level {data.get('level', 0)}"
            coverage = f"{int(data.get('coverage', 0) * 100)}%" if 'coverage' in data else 'N/A'
            summary.append({'name': name, 'status': status, 'coverage': coverage})
        return summary


# ============================================
# ВСЕЛЕНА SARAKT
# ============================================

class SaraktUniverse:
    """Главен клас за управление на вселената Sarakt"""
    
    def __init__(self):
        self.planets: List[Planet] = []
        self.cities: List[City] = []
        self.npcs: List[NPC] = []
        self.factions: List[Dict] = []
        self.current_cycle = 0
        
        self._initialize()
    
    def _initialize(self):
        """Инициализира системата Sarakt"""
        print('🌌 Инициализиране на системата Sarakt...\n')
        
        # Създава Sarakt (главна обитаема планета)
        sarakt = Planet(1, 'Sarakt', 12345, PlanetType.HABITABLE_PRIMARY, True)
        self.planets.append(sarakt)
        print('✅ Планета създадена: Sarakt (Главна обитаема)')
        
        # Създава Octavia Capital City на Sarakt
        octavia = City(1, 'Octavia Capital City', 1, 10000)
        self.cities.append(octavia)
        print('🏛️  Град основан: Octavia Capital City (10,000 парцела)')
        
        # Създава Zythera (биотех хаос)
        zythera = Planet(2, 'Zythera', 67890, PlanetType.HABITABLE_BIOTECH, True)
        self.planets.append(zythera)
        print('✅ Планета създадена: Zythera (Биотех хаос)')
        
        # Създава 20 минни планети
        for i in range(1, 21):
            planet = Planet(
                i + 2,
                f'Mining Planet {i}',
                100000 + i,
                PlanetType.MINING_STANDARD,
                False
            )
            self.planets.append(planet)
        print('⛏️  Създадени 20 минни планети')
        
        # Създава начални NPCs с Dynasty Dulo наследство
        print('\n👥 Създаване на Dynasty Dulo потомци...')
        for i in range(100):
            npc = NPC(i + 1, 1, 50000 + i)  # Повечето на Sarakt
            self.npcs.append(npc)
        print(f'✅ Създадени {len(self.npcs)} NPCs')
        
        print('\n✨ Система Sarakt инициализирана!\n')
    
    def simulate_cycle(self):
        """Симулира един цикъл"""
        self.current_cycle += 1
        
        # Остарява всички NPCs
        for npc in self.npcs:
            npc.age_cycle()
        
        # Актуализира икономика на градовете
        for city in self.cities:
            city._update_city_stats()
    
    def simulate_multiple_cycles(self, cycles: int):
        """Симулира множество цикли"""
        print(f'\n⚙️  Симулиране на {cycles} цикъла...\n')
        for _ in range(cycles):
            self.simulate_cycle()
        print('✅ Симулация завършена\n')
    
    def get_planet(self, identifier) -> Optional[Planet]:
        """Взима планета по име или ID"""
        if isinstance(identifier, str):
            return next((p for p in self.planets if p.name == identifier), None)
        return next((p for p in self.planets if p.id == identifier), None)
    
    def get_city(self, identifier) -> Optional[City]:
        """Взима град по име или ID"""
        if isinstance(identifier, str):
            return next((c for c in self.cities if c.name == identifier), None)
        return next((c for c in self.cities if c.id == identifier), None)
    
    def get_npc(self, npc_id: int) -> Optional[NPC]:
        """Взима NPC по ID"""
        return next((npc for npc in self.npcs if npc.id == npc_id), None)
    
    def get_universe_status(self) -> Dict:
        """Връща статус на вселената"""
        return {
            'cycle': self.current_cycle,
            'total_planets': len(self.planets),
            'habitable_planets': sum(1 for p in self.planets if p.is_habitable),
            'total_cities': len(self.cities),
            'total_npcs': len(self.npcs),
            'mature_npcs': sum(1 for npc in self.npcs if npc.state == NPCState.MATURE),
            'loyal_npcs': sum(1 for npc in self.npcs if npc.state == NPCState.LOYAL)
        }


# ============================================
# ДЕМО
# ============================================

if __name__ == '__main__':
    # Създава вселената
    universe = SaraktUniverse()
    
    # Симулира 20 цикъла
    universe.simulate_multiple_cycles(20)
    
    # Показва статус
    print('═' * 50)
    print('СТАТУС НА СИСТЕМА SARAKT')
    print('═' * 50)
    print(json.dumps(universe.get_universe_status(), indent=2, ensure_ascii=False))
    
    # Показва детайли за Sarakt
    print('\n' + '═' * 50)
    print('ПЛАНЕТА: SARAKT')
    print('═' * 50)
    sarakt = universe.get_planet('Sarakt')
    print(f'Свойства: {sarakt.properties}')
    print(f'Биоми: {len(sarakt.biomes)}')
    print(f'Топ ресурси: {sarakt.get_resource_summary()[:10]}')
    
    # Показва статистики на Octavia
    print('\n' + '═' * 50)
    print('ГРАД: OCTAVIA CAPITAL CITY')
    print('═' * 50)
    octavia = universe.get_city('Octavia Capital City')
    print(json.dumps(octavia.get_city_stats(), indent=2, ensure_ascii=False))
    
    # Показва примери с NPCs
    print('\n' + '═' * 50)
    print('NPC ПРИМЕРИ (Dynasty Dulo потомци)')
    print('═' * 50)
    for npc in universe.npcs[:5]:
        print(f'\n{npc.get_name()} (ID: {npc.id})')
        print(f'Възраст: {npc.age}, Състояние: {npc.state.value}, Поколение: {npc.generation}')
        if npc.personality:
            print(f'Топ умения: {npc.get_top_skills(3)}')
