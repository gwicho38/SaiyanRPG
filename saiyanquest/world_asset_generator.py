#!/usr/bin/env python3
"""
World Asset Generator - Expands existing world themes with new matching assets
Creates procedural assets that match the style and theme of existing worlds
"""

import random
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class WorldTheme:
    """Represents a world theme with its characteristics"""
    def __init__(self, name: str, color_scheme: str, atmosphere: str, 
                 building_types: List[str], unique_features: List[str]):
        self.name = name
        self.color_scheme = color_scheme
        self.atmosphere = atmosphere
        self.building_types = building_types
        self.unique_features = unique_features

class WorldAssetGenerator:
    """Generates new assets that match existing world themes"""
    
    def __init__(self):
        self.world_themes = {
            'candy': WorldTheme(
                name='Candy World',
                color_scheme='bright_pastels',
                atmosphere='sweet_whimsical',
                building_types=['hospital', 'cafe', 'house', 'inn', 'center', 'port', 'scoop'],
                unique_features=['candy_cane_streets', 'gingerbread_houses', 'chocolate_rivers', 'sugar_crystal_formations']
            ),
            'flower': WorldTheme(
                name='Flower City',
                color_scheme='natural_greens_pinks',
                atmosphere='peaceful_botanical',
                building_types=['center', 'house', 'petshop', 'scoop', 'city'],
                unique_features=['blooming_gardens', 'petal_pathways', 'greenhouse_districts', 'flower_fountains']
            ),
            'leather': WorldTheme(
                name='Leather Town',
                color_scheme='earth_browns',
                atmosphere='rustic_craftsmanship',
                building_types=['center', 'gym', 'house', 'museum', 'scoop', 'shaft', 'town'],
                unique_features=['leather_workshops', 'tanning_facilities', 'craft_markets', 'tool_forges']
            ),
            'timber': WorldTheme(
                name='Timber Settlement',
                color_scheme='wood_greens',
                atmosphere='forestry_natural',
                building_types=['cafe', 'center', 'house', 'scoop', 'town', 'walledgarden'],
                unique_features=['lumber_mills', 'tree_houses', 'forest_clearings', 'wooden_bridges']
            ),
            'paper': WorldTheme(
                name='Paper District',
                color_scheme='clean_whites_blues',
                atmosphere='scholarly_bureaucratic',
                building_types=['daycare', 'manor', 'rival_bedroom', 'rival_downstairs', 'rival_office', 'scoop', 'town'],
                unique_features=['libraries', 'printing_presses', 'document_archives', 'study_halls']
            ),
            'cotton': WorldTheme(
                name='Cotton Fields',
                color_scheme='soft_whites_creams',
                atmosphere='agricultural_pastoral',
                building_types=['cafe', 'cathedral', 'daycare', 'misa_house', 'scoop', 'town', 'underground'],
                unique_features=['cotton_fields', 'textile_mills', 'spinning_wheels', 'fabric_markets']
            ),
            'crystal': WorldTheme(
                name='Crystal Town',
                color_scheme='crystal_blues_purples',
                atmosphere='mystical_technological',
                building_types=['bank', 'center', 'town_cafe', 'town_house', 'town'],
                unique_features=['crystal_spires', 'energy_conduits', 'gem_mines', 'crystal_formations']
            ),
            'azure': WorldTheme(
                name='Azure Kingdom',
                color_scheme='deep_blues_silvers',
                atmosphere='regal_sophisticated',
                building_types=['town_hall', 'town'],
                unique_features=['royal_palaces', 'azure_fountains', 'noble_districts', 'ceremonial_halls']
            ),
        }
        
        # Common GTA building types that can be themed
        self.gta_building_types = [
            'police_station', 'fire_station', 'hospital', 'bank', 'garage', 'warehouse',
            'nightclub', 'restaurant', 'shop', 'apartment', 'office_building', 'school',
            'park', 'marina', 'airport', 'stadium', 'casino', 'mall', 'gas_station',
            'car_dealership', 'construction_site', 'industrial_complex', 'subway_station'
        ]
        
        # Residential variations
        self.residential_types = [
            'mansion', 'apartment_complex', 'townhouse', 'villa', 'cottage', 'penthouse',
            'suburban_house', 'beach_house', 'farmhouse', 'loft', 'duplex'
        ]
        
        # Commercial variations  
        self.commercial_types = [
            'shopping_center', 'strip_mall', 'department_store', 'boutique', 'market',
            'food_court', 'cinema', 'arcade', 'bookstore', 'electronics_store'
        ]

    def generate_theme_expansions(self, theme_name: str, expansion_count: int = 10) -> List[Dict]:
        """Generate new assets for a specific theme"""
        if theme_name not in self.world_themes:
            raise ValueError(f"Unknown theme: {theme_name}")
            
        theme = self.world_themes[theme_name]
        expansions = []
        
        for i in range(expansion_count):
            asset_type = random.choice(['residential', 'commercial', 'industrial', 'civic', 'unique'])
            asset_name = self._generate_themed_asset_name(theme, asset_type, i)
            asset_data = self._generate_asset_data(theme, asset_type, asset_name)
            
            expansions.append(asset_data)
            
        return expansions
    
    def _generate_themed_asset_name(self, theme: WorldTheme, asset_type: str, index: int) -> str:
        """Generate a themed asset name"""
        theme_prefix = theme.name.lower().split()[0]
        
        if asset_type == 'residential':
            building = random.choice(self.residential_types)
            variant = random.choice(['north', 'south', 'east', 'west', 'central', 'upper', 'lower'])
            return f"{theme_prefix}_{variant}_{building}"
            
        elif asset_type == 'commercial':
            building = random.choice(self.commercial_types)
            variant = random.choice(['main', 'plaza', 'district', 'corner', 'grand'])
            return f"{theme_prefix}_{variant}_{building}"
            
        elif asset_type == 'industrial':
            building = random.choice(['factory', 'warehouse', 'plant', 'facility', 'complex'])
            variant = random.choice(['processing', 'manufacturing', 'storage', 'distribution'])
            return f"{theme_prefix}_{variant}_{building}"
            
        elif asset_type == 'civic':
            building = random.choice(self.gta_building_types[:12])  # First 12 are civic
            return f"{theme_prefix}_{building}"
            
        else:  # unique
            feature = random.choice(theme.unique_features)
            variant = random.choice(['alpha', 'beta', 'gamma', 'prime', 'central'])
            return f"{theme_prefix}_{feature}_{variant}".replace(' ', '_')
    
    def _generate_asset_data(self, theme: WorldTheme, asset_type: str, asset_name: str) -> Dict:
        """Generate complete asset data"""
        return {
            'name': asset_name,
            'theme': theme.name,
            'type': asset_type,
            'color_scheme': theme.color_scheme,
            'atmosphere': theme.atmosphere,
            'size': self._get_asset_size(asset_type),
            'description': self._generate_description(theme, asset_type, asset_name),
            'features': self._generate_features(theme, asset_type),
            'connections': self._get_required_connections(asset_type),
            'gta_elements': self._get_gta_elements(asset_type)
        }
    
    def _get_asset_size(self, asset_type: str) -> Tuple[int, int]:
        """Get appropriate size for asset type"""
        size_ranges = {
            'residential': [(15, 20), (20, 25), (25, 30)],
            'commercial': [(20, 30), (30, 40), (40, 50)],
            'industrial': [(30, 40), (40, 60), (50, 80)],
            'civic': [(25, 35), (35, 45), (40, 60)],
            'unique': [(20, 40), (40, 60), (60, 100)]
        }
        return random.choice(size_ranges.get(asset_type, [(20, 20), (30, 30)]))
    
    def _generate_description(self, theme: WorldTheme, asset_type: str, asset_name: str) -> str:
        """Generate asset description"""
        descriptions = {
            'residential': f"A {theme.atmosphere} residential area in {theme.name}",
            'commercial': f"A bustling {theme.atmosphere} commercial district", 
            'industrial': f"An industrial {theme.atmosphere} facility",
            'civic': f"A civic building serving the {theme.name} community",
            'unique': f"A unique {theme.atmosphere} landmark"
        }
        return descriptions.get(asset_type, f"A {theme.atmosphere} structure")
    
    def _generate_features(self, theme: WorldTheme, asset_type: str) -> List[str]:
        """Generate asset-specific features"""
        base_features = random.sample(theme.unique_features, min(2, len(theme.unique_features)))
        
        gta_features = {
            'residential': ['parking', 'balconies', 'gardens', 'security_gates'],
            'commercial': ['storefronts', 'neon_signs', 'parking_lots', 'loading_docks'],
            'industrial': ['smokestacks', 'conveyor_belts', 'storage_tanks', 'loading_bays'],
            'civic': ['public_access', 'official_signage', 'security_checkpoints', 'parking'],
            'unique': ['tourist_attraction', 'photo_spots', 'special_effects', 'unique_architecture']
        }
        
        asset_features = random.sample(gta_features.get(asset_type, []), 2)
        return base_features + asset_features
    
    def _get_required_connections(self, asset_type: str) -> List[str]:
        """Get required road/transit connections"""
        connections = {
            'residential': ['local_roads', 'pedestrian_paths'],
            'commercial': ['main_roads', 'parking_access', 'pedestrian_areas'],
            'industrial': ['cargo_roads', 'rail_access', 'utility_connections'],
            'civic': ['main_roads', 'public_transit', 'emergency_access'],
            'unique': ['tourist_routes', 'scenic_roads', 'pedestrian_access']
        }
        return connections.get(asset_type, ['standard_roads'])
    
    def _get_gta_elements(self, asset_type: str) -> List[str]:
        """Get GTA-style gameplay elements"""
        elements = {
            'residential': ['hideout_potential', 'rooftop_access', 'escape_routes'],
            'commercial': ['shop_interactions', 'robbery_targets', 'crowd_areas'],
            'industrial': ['vehicle_spawns', 'explosive_barrels', 'crane_operations'],
            'civic': ['mission_locations', 'wanted_level_triggers', 'official_vehicles'],
            'unique': ['special_missions', 'collectible_locations', 'easter_eggs']
        }
        return elements.get(asset_type, ['standard_interactions'])

    def generate_comprehensive_expansions(self) -> Dict[str, List[Dict]]:
        """Generate comprehensive expansions with many more assets per theme"""
        print("🎨 Generating Comprehensive World Expansions")
        print("=" * 60)
        
        all_expansions = {}
        
        # Generate different amounts based on theme development
        expansion_counts = {
            'candy': 25,    # Most developed theme
            'leather': 20,  # Well developed
            'cotton': 18,   # Good foundation
            'flower': 15,   # Moderate development
            'timber': 15,   # Moderate development
            'paper': 12,    # Some development
            'crystal': 20,  # Needs major expansion
            'azure': 22,    # Minimal - major expansion needed
        }
        
        for theme_name, count in expansion_counts.items():
            print(f"🌍 Generating {count} comprehensive assets for {theme_name.title()} World...")
            
            # Generate specialized asset categories
            expansions = []
            
            # Infrastructure (25% of assets)
            infrastructure_count = max(1, count // 4)
            expansions.extend(self._generate_infrastructure_assets(theme_name, infrastructure_count))
            
            # Residential districts (30% of assets)
            residential_count = max(1, count * 3 // 10)
            expansions.extend(self._generate_residential_districts(theme_name, residential_count))
            
            # Commercial areas (25% of assets)
            commercial_count = max(1, count // 4)
            expansions.extend(self._generate_commercial_districts(theme_name, commercial_count))
            
            # Entertainment & leisure (10% of assets)
            entertainment_count = max(1, count // 10)
            expansions.extend(self._generate_entertainment_venues(theme_name, entertainment_count))
            
            # Unique landmarks (10% of assets)
            landmark_count = max(1, count // 10)
            expansions.extend(self._generate_unique_landmarks(theme_name, landmark_count))
            
            # Fill remaining slots with mixed assets
            remaining = count - len(expansions)
            if remaining > 0:
                mixed_assets = self.generate_theme_expansions(theme_name, remaining)
                expansions.extend(mixed_assets)
            
            # Trim to exact count
            expansions = expansions[:count]
            all_expansions[theme_name] = expansions
            
            # Show breakdown
            types = {}
            for asset in expansions:
                asset_type = asset['type']
                types[asset_type] = types.get(asset_type, 0) + 1
            
            print(f"   📊 Breakdown: {', '.join(f'{k}: {v}' for k, v in sorted(types.items()))}")
            
            # Show some examples
            for i, asset in enumerate(expansions[:3]):
                print(f"   {i+1}. {asset['name']} ({asset['type']}) - {asset['description']}")
            if len(expansions) > 3:
                print(f"   ... and {len(expansions)-3} more")
        
        total_assets = sum(len(assets) for assets in all_expansions.values())
        print(f"\n🎉 Generated {total_assets} total comprehensive world assets!")
        
        return all_expansions

    def _generate_infrastructure_assets(self, theme_name: str, count: int) -> List[Dict]:
        """Generate infrastructure assets (utilities, transport, services)"""
        theme = self.world_themes[theme_name]
        assets = []
        
        infrastructure_types = [
            'power_plant', 'water_treatment', 'subway_station', 'bus_depot',
            'fire_station', 'police_station', 'hospital', 'school',
            'post_office', 'city_hall', 'courthouse', 'library',
            'waste_management', 'telecommunications', 'maintenance_yard'
        ]
        
        for i in range(count):
            infra_type = random.choice(infrastructure_types)
            district = random.choice(['north', 'south', 'east', 'west', 'central'])
            name = f"{theme_name}_{district}_{infra_type}"
            
            assets.append({
                'name': name,
                'theme': theme.name,
                'type': 'infrastructure',
                'subtype': infra_type,
                'color_scheme': theme.color_scheme,
                'atmosphere': theme.atmosphere,
                'size': (30 + random.randint(-10, 20), 25 + random.randint(-5, 15)),
                'description': f"Essential {infra_type.replace('_', ' ')} serving {theme.name}",
                'features': self._get_infrastructure_features(infra_type, theme),
                'connections': ['main_roads', 'utility_lines', 'emergency_access'],
                'gta_elements': self._get_infrastructure_gta_elements(infra_type)
            })
        
        return assets

    def _generate_residential_districts(self, theme_name: str, count: int) -> List[Dict]:
        """Generate residential district assets"""
        theme = self.world_themes[theme_name]
        assets = []
        
        residential_styles = [
            'luxury_condos', 'apartment_complex', 'townhouse_row', 'suburban_homes',
            'high_rise_towers', 'gated_community', 'artist_lofts', 'student_housing',
            'senior_living', 'family_neighborhood', 'mansion_district', 'waterfront_homes'
        ]
        
        for i in range(count):
            style = random.choice(residential_styles)
            district = random.choice(['heights', 'gardens', 'hills', 'plaza', 'park', 'bay'])
            name = f"{theme_name}_{district}_{style}"
            
            assets.append({
                'name': name,
                'theme': theme.name,
                'type': 'residential_district',
                'subtype': style,
                'color_scheme': theme.color_scheme,
                'atmosphere': theme.atmosphere,
                'size': (40 + random.randint(-15, 25), 35 + random.randint(-10, 20)),
                'description': f"Residential {style.replace('_', ' ')} in {theme.name} style",
                'features': self._get_residential_features(style, theme),
                'connections': ['residential_roads', 'pedestrian_paths', 'public_transit'],
                'gta_elements': ['hideout_potential', 'rooftop_access', 'garage_spawns', 'safe_houses']
            })
        
        return assets

    def _generate_commercial_districts(self, theme_name: str, count: int) -> List[Dict]:
        """Generate commercial district assets"""
        theme = self.world_themes[theme_name]
        assets = []
        
        commercial_types = [
            'shopping_mall', 'business_district', 'market_square', 'entertainment_complex',
            'restaurant_row', 'fashion_quarter', 'tech_hub', 'artisan_market',
            'financial_center', 'trade_plaza', 'retail_park', 'boutique_district'
        ]
        
        for i in range(count):
            comm_type = random.choice(commercial_types)
            location = random.choice(['downtown', 'uptown', 'midtown', 'plaza', 'center', 'square'])
            name = f"{theme_name}_{location}_{comm_type}"
            
            assets.append({
                'name': name,
                'theme': theme.name,
                'type': 'commercial_district',
                'subtype': comm_type,
                'color_scheme': theme.color_scheme,
                'atmosphere': theme.atmosphere,
                'size': (50 + random.randint(-15, 30), 40 + random.randint(-10, 25)),
                'description': f"Bustling {comm_type.replace('_', ' ')} with {theme.atmosphere} character",
                'features': self._get_commercial_features(comm_type, theme),
                'connections': ['main_roads', 'parking_lots', 'pedestrian_areas', 'delivery_access'],
                'gta_elements': ['robbery_targets', 'chase_sequences', 'crowd_interactions', 'shop_missions']
            })
        
        return assets

    def _generate_entertainment_venues(self, theme_name: str, count: int) -> List[Dict]:
        """Generate entertainment and leisure assets"""
        theme = self.world_themes[theme_name]
        assets = []
        
        entertainment_types = [
            'theme_park', 'sports_stadium', 'concert_hall', 'casino',
            'nightclub_district', 'beach_resort', 'golf_course', 'spa_retreat',
            'adventure_park', 'cultural_center', 'festival_grounds', 'marina'
        ]
        
        for i in range(count):
            ent_type = random.choice(entertainment_types)
            name = f"{theme_name}_grand_{ent_type}"
            
            assets.append({
                'name': name,
                'theme': theme.name,
                'type': 'entertainment',
                'subtype': ent_type,
                'color_scheme': theme.color_scheme,
                'atmosphere': theme.atmosphere,
                'size': (60 + random.randint(-20, 40), 50 + random.randint(-15, 35)),
                'description': f"Premier {ent_type.replace('_', ' ')} destination in {theme.name}",
                'features': self._get_entertainment_features(ent_type, theme),
                'connections': ['tourist_routes', 'vip_access', 'public_transit', 'event_parking'],
                'gta_elements': ['mission_locations', 'special_events', 'celebrity_encounters', 'heist_targets']
            })
        
        return assets

    def _generate_unique_landmarks(self, theme_name: str, count: int) -> List[Dict]:
        """Generate unique landmark assets specific to each theme"""
        theme = self.world_themes[theme_name]
        assets = []
        
        # Theme-specific landmark types
        landmark_types = {
            'candy': ['candy_castle', 'chocolate_waterfall', 'gum_drop_mountain', 'sugar_crystal_cave'],
            'flower': ['botanical_dome', 'flower_tower', 'petal_fountain', 'rainbow_garden'],
            'leather': ['craft_monument', 'leather_guild_hall', 'artisan_workshop', 'tanning_tower'],
            'timber': ['great_tree', 'lumber_monument', 'forest_cathedral', 'wooden_skybridge'],
            'paper': ['knowledge_tower', 'grand_library', 'scroll_monument', 'printing_cathedral'],
            'cotton': ['textile_spire', 'spinning_wheel_plaza', 'cotton_field_vista', 'weaving_hall'],
            'crystal': ['crystal_spire', 'energy_nexus', 'gem_cathedral', 'prism_tower'],
            'azure': ['royal_palace', 'azure_monument', 'noble_observatory', 'ceremonial_grounds']
        }
        
        theme_landmarks = landmark_types.get(theme_name, ['monument', 'landmark', 'memorial', 'plaza'])
        
        for i in range(count):
            landmark = random.choice(theme_landmarks)
            modifier = random.choice(['grand', 'ancient', 'sacred', 'legendary', 'mystical'])
            name = f"{theme_name}_{modifier}_{landmark}"
            
            assets.append({
                'name': name,
                'theme': theme.name,
                'type': 'unique_landmark',
                'subtype': landmark,
                'color_scheme': theme.color_scheme,
                'atmosphere': theme.atmosphere,
                'size': (80 + random.randint(-30, 50), 70 + random.randint(-25, 45)),
                'description': f"Iconic {landmark.replace('_', ' ')} representing the essence of {theme.name}",
                'features': theme.unique_features + [f"{landmark}_features", "tourist_attraction", "photo_opportunity"],
                'connections': ['scenic_routes', 'tourist_paths', 'ceremonial_access'],
                'gta_elements': ['collectible_locations', 'easter_eggs', 'special_missions', 'photo_challenges']
            })
        
        return assets

    def _get_infrastructure_features(self, infra_type: str, theme: WorldTheme) -> List[str]:
        """Get infrastructure-specific features"""
        base_features = random.sample(theme.unique_features, min(1, len(theme.unique_features)))
        
        infra_features = {
            'power_plant': ['generators', 'transformers', 'control_room'],
            'police_station': ['holding_cells', 'evidence_room', 'dispatch_center'],
            'hospital': ['emergency_room', 'operating_theaters', 'ambulance_bay'],
            'school': ['classrooms', 'gymnasium', 'playground'],
        }
        
        specific_features = infra_features.get(infra_type, ['administrative_offices', 'parking'])
        return base_features + specific_features

    def _get_infrastructure_gta_elements(self, infra_type: str) -> List[str]:
        """Get GTA gameplay elements for infrastructure"""
        elements = {
            'police_station': ['wanted_level_triggers', 'mission_briefings', 'vehicle_impound'],
            'hospital': ['health_recovery', 'respawn_point', 'medical_missions'],
            'fire_station': ['fire_truck_spawns', 'emergency_missions', 'rescue_operations'],
            'school': ['chase_sequences', 'crowd_areas', 'student_missions'],
        }
        return elements.get(infra_type, ['standard_interactions', 'mission_potential'])

    def _get_residential_features(self, style: str, theme: WorldTheme) -> List[str]:
        """Get residential-specific features"""
        base_features = random.sample(theme.unique_features, min(1, len(theme.unique_features)))
        
        style_features = {
            'luxury_condos': ['concierge', 'rooftop_pool', 'valet_parking'],
            'apartment_complex': ['courtyard', 'laundry_facilities', 'community_center'],
            'mansion_district': ['private_gardens', 'security_gates', 'staff_quarters'],
            'student_housing': ['study_rooms', 'common_areas', 'bike_storage'],
        }
        
        specific_features = style_features.get(style, ['parking', 'gardens', 'mailboxes'])
        return base_features + specific_features

    def _get_commercial_features(self, comm_type: str, theme: WorldTheme) -> List[str]:
        """Get commercial-specific features"""
        base_features = random.sample(theme.unique_features, min(2, len(theme.unique_features)))
        
        comm_features = {
            'shopping_mall': ['food_court', 'department_stores', 'multi_level_parking'],
            'business_district': ['office_towers', 'conference_centers', 'corporate_plazas'],
            'market_square': ['vendor_stalls', 'central_fountain', 'performance_area'],
            'restaurant_row': ['outdoor_dining', 'culinary_variety', 'late_night_venues'],
        }
        
        specific_features = comm_features.get(comm_type, ['storefronts', 'customer_parking'])
        return base_features + specific_features

    def _get_entertainment_features(self, ent_type: str, theme: WorldTheme) -> List[str]:
        """Get entertainment-specific features"""
        base_features = random.sample(theme.unique_features, min(2, len(theme.unique_features)))
        
        ent_features = {
            'theme_park': ['roller_coasters', 'themed_areas', 'gift_shops'],
            'sports_stadium': ['playing_field', 'luxury_boxes', 'concession_stands'],
            'casino': ['gaming_floors', 'high_roller_suites', 'entertainment_shows'],
            'nightclub_district': ['dance_floors', 'VIP_areas', 'rooftop_bars'],
        }
        
        specific_features = ent_features.get(ent_type, ['entertainment_facilities', 'guest_services'])
        return base_features + specific_features

    def generate_all_theme_expansions(self, expansion_count_per_theme: int = 15) -> Dict[str, List[Dict]]:
        """Generate expansions for all themes"""
        print("🎨 Generating World Asset Expansions")
        print("=" * 50)
        
        all_expansions = {}
        
        for theme_name in self.world_themes.keys():
            print(f"🌍 Generating {expansion_count_per_theme} assets for {theme_name.title()} World...")
            expansions = self.generate_theme_expansions(theme_name, expansion_count_per_theme)
            all_expansions[theme_name] = expansions
            
            # Show some examples
            for i, asset in enumerate(expansions[:3]):
                print(f"   {i+1}. {asset['name']} ({asset['type']}) - {asset['description']}")
            if len(expansions) > 3:
                print(f"   ... and {len(expansions)-3} more")
            
        total_assets = sum(len(assets) for assets in all_expansions.values())
        print(f"\n✅ Generated {total_assets} total new world assets across {len(all_expansions)} themes!")
        
        return all_expansions

    def create_asset_implementation_plan(self, expansions: Dict[str, List[Dict]]) -> Dict:
        """Create implementation plan for the generated assets"""
        plan = {
            'summary': {
                'total_themes': len(expansions),
                'total_assets': sum(len(assets) for assets in expansions.values()),
                'asset_breakdown': {}
            },
            'implementation_priority': [],
            'integration_notes': [],
            'technical_requirements': []
        }
        
        # Asset breakdown by type
        for theme_name, assets in expansions.items():
            type_counts = {}
            for asset in assets:
                asset_type = asset['type']
                type_counts[asset_type] = type_counts.get(asset_type, 0) + 1
            plan['summary']['asset_breakdown'][theme_name] = type_counts
        
        # Implementation priority (most developed themes first)
        theme_priorities = [
            ('candy', 'Most developed - many existing assets'),
            ('leather', 'Well developed - good variety'),
            ('cotton', 'Good foundation - multiple buildings'),
            ('flower', 'Moderate development'),
            ('timber', 'Moderate development'), 
            ('paper', 'Some development'),
            ('crystal', 'Limited - needs expansion'),
            ('azure', 'Minimal - major expansion needed')
        ]
        
        plan['implementation_priority'] = theme_priorities
        
        # Integration notes
        plan['integration_notes'] = [
            "New assets should be positioned near existing themed areas",
            "Maintain consistent color schemes and architectural styles",
            "Ensure proper road connections to new buildings",
            "Add appropriate NPCs and vehicles for each theme",
            "Include GTA-style interactive elements and missions"
        ]
        
        # Technical requirements
        plan['technical_requirements'] = [
            "TMX map file generation for each asset",
            "Tileset integration matching existing themes",
            "Collision detection setup",
            "Entity placement (NPCs, vehicles, items)",
            "Mission trigger integration",
            "World streamer integration for proper loading"
        ]
        
        return plan

if __name__ == "__main__":
    generator = WorldAssetGenerator()
    expansions = generator.generate_all_theme_expansions(8)
    plan = generator.create_asset_implementation_plan(expansions)
    
    print(f"\n📋 Implementation Plan:")
    print(f"   Priority Order: {len(plan['implementation_priority'])} themes")
    print(f"   Technical Tasks: {len(plan['technical_requirements'])} requirements")
    print(f"   Integration Notes: {len(plan['integration_notes'])} guidelines")