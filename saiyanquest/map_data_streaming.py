#!/usr/bin/env python3
"""
Map Data Loading and Streaming System - Based on Carnage3D Architecture
Provides efficient loading and streaming of large open world maps with LOD management.
"""

import pygame
import json
import pickle
import threading
import time
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from abc import ABC, abstractmethod
import asyncio
import concurrent.futures
from collections import defaultdict, deque

from .world_3d_system import Vector3, WorldObject3D, RenderLayer


class MapDataFormat(Enum):
    """Supported map data formats"""
    TMX = "tmx"           # Tiled TMX format
    JSON = "json"         # Custom JSON format  
    BINARY = "bin"        # Optimized binary format
    YAML = "yaml"         # YAML configuration format
    GTA_MAP = "gta_map"   # GTA-style map format

class StreamingState(Enum):
    """States for map chunk streaming"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    UNLOADING = "unloading"
    ERROR = "error"

class LODLevel(IntEnum):
    """Level of detail for map objects and geometry"""
    ULTRA_HIGH = 0    # Player's immediate vicinity
    HIGH = 1          # Near player
    MEDIUM = 2        # Visible distance
    LOW = 3           # Far distance 
    VERY_LOW = 4      # Distant background

@dataclass
class MapChunk:
    """A chunk of map data for streaming"""
    chunk_id: str
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    center: Vector3
    lod_level: LODLevel = LODLevel.LOW
    state: StreamingState = StreamingState.UNLOADED
    
    # Map data
    tile_layers: Dict[str, Any] = field(default_factory=dict)
    objects: List[WorldObject3D] = field(default_factory=list)
    collision_data: Dict[Tuple[int, int], bool] = field(default_factory=dict)
    surface_data: Optional[pygame.Surface] = None
    
    # Performance tracking
    load_time: float = 0.0
    last_access_time: float = 0.0
    memory_usage: int = 0  # bytes
    
    # Streaming metadata
    dependencies: Set[str] = field(default_factory=set)  # Other chunks this depends on
    file_path: Optional[Path] = None
    checksum: Optional[str] = None

@dataclass  
class MapMetadata:
    """Metadata for an entire map"""
    map_name: str
    world_bounds: Tuple[int, int, int, int]
    chunk_size: int = 512  # Size of each chunk in world units
    total_chunks: int = 0
    file_format: MapDataFormat = MapDataFormat.TMX
    
    # Asset references
    tilesets: List[str] = field(default_factory=list)
    textures: List[str] = field(default_factory=list) 
    models: List[str] = field(default_factory=list)
    sounds: List[str] = field(default_factory=list)
    
    # Streaming configuration
    preload_radius: int = 2  # Chunks to preload around player
    unload_distance: int = 4  # Distance at which to unload chunks
    max_concurrent_loads: int = 3
    
    # Version and validation
    version: str = "1.0"
    created_timestamp: float = 0.0
    modified_timestamp: float = 0.0

class MapDataLoader(ABC):
    """Abstract base class for map data loaders"""
    
    @abstractmethod
    def load_metadata(self, map_path: Path) -> Optional[MapMetadata]:
        """Load map metadata"""
        pass
    
    @abstractmethod
    def load_chunk(self, chunk_id: str, metadata: MapMetadata) -> Optional[MapChunk]:
        """Load a specific map chunk"""
        pass
    
    @abstractmethod 
    def save_chunk(self, chunk: MapChunk, metadata: MapMetadata) -> bool:
        """Save a map chunk"""
        pass

class TMXMapDataLoader(MapDataLoader):
    """Loader for TMX (Tiled) map data"""
    
    def __init__(self, maps_directory: Path):
        self.maps_directory = maps_directory
        self.tileset_cache: Dict[str, pygame.Surface] = {}
        
    def load_metadata(self, map_path: Path) -> Optional[MapMetadata]:
        """Load TMX map metadata"""
        try:
            import pytmx
            
            tmx_map = pytmx.load_pygame(str(map_path))
            
            # Calculate world bounds and chunk count
            world_width = tmx_map.width * tmx_map.tilewidth
            world_height = tmx_map.height * tmx_map.tileheight
            chunk_size = 512  # Default chunk size
            
            chunks_x = math.ceil(world_width / chunk_size)
            chunks_y = math.ceil(world_height / chunk_size)
            total_chunks = chunks_x * chunks_y
            
            # Extract tileset information
            tilesets = [ts.name for ts in tmx_map.tilesets]
            
            metadata = MapMetadata(
                map_name=map_path.stem,
                world_bounds=(0, 0, world_width, world_height),
                chunk_size=chunk_size,
                total_chunks=total_chunks,
                file_format=MapDataFormat.TMX,
                tilesets=tilesets,
                created_timestamp=map_path.stat().st_ctime,
                modified_timestamp=map_path.stat().st_mtime
            )
            
            print(f"📄 Loaded TMX metadata: {metadata.map_name} ({chunks_x}x{chunks_y} chunks)")
            return metadata
            
        except Exception as e:
            print(f"❌ Failed to load TMX metadata from {map_path}: {e}")
            return None
    
    def load_chunk(self, chunk_id: str, metadata: MapMetadata) -> Optional[MapChunk]:
        """Load a TMX map chunk"""
        try:
            # Parse chunk ID to get coordinates
            parts = chunk_id.split('_')
            chunk_x, chunk_y = int(parts[-2]), int(parts[-1])
            
            # Calculate chunk bounds
            x = chunk_x * metadata.chunk_size
            y = chunk_y * metadata.chunk_size
            bounds = (x, y, metadata.chunk_size, metadata.chunk_size)
            center = Vector3(x + metadata.chunk_size/2, 0, y + metadata.chunk_size/2)
            
            # Load the actual map data (simplified for demo)
            chunk = MapChunk(
                chunk_id=chunk_id,
                bounds=bounds,
                center=center,
                file_path=self.maps_directory / f"{metadata.map_name}.tmx"
            )
            
            # For demo purposes, create some basic tile data
            chunk.tile_layers["ground"] = self._generate_demo_tiles(bounds)
            chunk.state = StreamingState.LOADED
            chunk.load_time = 0.1  # Simulated load time
            
            print(f"🗂️ Loaded TMX chunk: {chunk_id} at {bounds}")
            return chunk
            
        except Exception as e:
            print(f"❌ Failed to load TMX chunk {chunk_id}: {e}")
            return None
    
    def save_chunk(self, chunk: MapChunk, metadata: MapMetadata) -> bool:
        """Save TMX chunk (not implemented for read-only TMX)"""
        return False
    
    def _generate_demo_tiles(self, bounds: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """Generate demo tile data for testing"""
        x, y, w, h = bounds
        tiles = {}
        
        # Create a simple pattern for demo
        for tile_y in range(0, h, 32):
            for tile_x in range(0, w, 32):
                world_x = x + tile_x
                world_y = y + tile_y
                
                # Simple grass/road pattern
                if (world_x // 32) % 10 == 0 or (world_y // 32) % 10 == 0:
                    tiles[(tile_x, tile_y)] = "road"
                else:
                    tiles[(tile_x, tile_y)] = "grass"
        
        return tiles

class BinaryMapDataLoader(MapDataLoader):
    """Optimized binary loader for large maps"""
    
    def __init__(self, maps_directory: Path):
        self.maps_directory = maps_directory
        
    def load_metadata(self, map_path: Path) -> Optional[MapMetadata]:
        """Load binary map metadata"""
        metadata_path = map_path.with_suffix('.meta')
        
        try:
            with metadata_path.open('rb') as f:
                metadata = pickle.load(f)
            
            print(f"📄 Loaded binary metadata: {metadata.map_name}")
            return metadata
            
        except Exception as e:
            print(f"❌ Failed to load binary metadata from {metadata_path}: {e}")
            return None
    
    def load_chunk(self, chunk_id: str, metadata: MapMetadata) -> Optional[MapChunk]:
        """Load binary map chunk"""
        chunk_path = self.maps_directory / metadata.map_name / f"{chunk_id}.chunk"
        
        try:
            with chunk_path.open('rb') as f:
                chunk = pickle.load(f)
            
            chunk.state = StreamingState.LOADED
            chunk.last_access_time = time.time()
            
            print(f"🗂️ Loaded binary chunk: {chunk_id}")
            return chunk
            
        except Exception as e:
            print(f"❌ Failed to load binary chunk {chunk_id}: {e}")
            return None
    
    def save_chunk(self, chunk: MapChunk, metadata: MapMetadata) -> bool:
        """Save binary chunk"""
        chunk_dir = self.maps_directory / metadata.map_name
        chunk_dir.mkdir(exist_ok=True)
        chunk_path = chunk_dir / f"{chunk.chunk_id}.chunk"
        
        try:
            with chunk_path.open('wb') as f:
                pickle.dump(chunk, f)
            
            print(f"💾 Saved binary chunk: {chunk.chunk_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save binary chunk {chunk.chunk_id}: {e}")
            return False

class MapStreamingManager:
    """Manages streaming of map data based on player position"""
    
    def __init__(self, maps_directory: Path):
        self.maps_directory = maps_directory
        self.current_metadata: Optional[MapMetadata] = None
        
        # Loaded chunks
        self.loaded_chunks: Dict[str, MapChunk] = {}
        self.active_chunks: Set[str] = set()
        self.loading_chunks: Set[str] = set()
        
        # Player tracking
        self.player_position = Vector3(0, 0, 0)
        self.player_chunk_id = ""
        
        # Streaming configuration
        self.max_loaded_chunks = 25
        self.preload_radius = 2
        self.unload_distance = 4
        self.max_concurrent_loads = 3
        
        # Data loaders
        self.loaders: Dict[MapDataFormat, MapDataLoader] = {
            MapDataFormat.TMX: TMXMapDataLoader(maps_directory),
            MapDataFormat.BINARY: BinaryMapDataLoader(maps_directory),
        }
        
        # Threading for background loading
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.loading_futures: Dict[str, concurrent.futures.Future] = {}
        
        # Performance tracking
        self.load_times: deque = deque(maxlen=100)
        self.memory_usage = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        print("🗺️ Map streaming manager initialized")
        print(f"   Max chunks: {self.max_loaded_chunks}")
        print(f"   Preload radius: {self.preload_radius}")
        print(f"   Concurrent loads: {self.max_concurrent_loads}")
    
    def load_map(self, map_name: str, format_type: MapDataFormat = MapDataFormat.TMX) -> bool:
        """Load a map and initialize streaming"""
        map_path = self._find_map_file(map_name, format_type)
        if not map_path:
            print(f"❌ Map file not found: {map_name}")
            return False
        
        loader = self.loaders.get(format_type)
        if not loader:
            print(f"❌ No loader for format: {format_type}")
            return False
        
        # Load metadata
        self.current_metadata = loader.load_metadata(map_path)
        if not self.current_metadata:
            print(f"❌ Failed to load map metadata: {map_name}")
            return False
        
        # Clear existing chunks
        self._unload_all_chunks()
        
        # Start initial loading around origin
        self.update_streaming(Vector3(0, 0, 0))
        
        print(f"✅ Map loaded: {map_name}")
        print(f"   Format: {format_type.value}")
        print(f"   Bounds: {self.current_metadata.world_bounds}")
        print(f"   Total chunks: {self.current_metadata.total_chunks}")
        
        return True
    
    def update_streaming(self, player_position: Vector3) -> None:
        """Update map streaming based on player position"""
        if not self.current_metadata:
            return
        
        self.player_position = player_position
        old_chunk_id = self.player_chunk_id
        self.player_chunk_id = self._get_chunk_id_for_position(player_position)
        
        # If player moved to a new chunk, update streaming
        if self.player_chunk_id != old_chunk_id:
            print(f"🚶 Player moved to chunk: {self.player_chunk_id}")
            self._update_chunk_loading()
        
        # Process completed loads
        self._process_loading_futures()
        
        # Unload distant chunks
        self._unload_distant_chunks()
        
        # Update LOD levels
        self._update_lod_levels()
    
    def _find_map_file(self, map_name: str, format_type: MapDataFormat) -> Optional[Path]:
        """Find map file with given name and format"""
        if format_type == MapDataFormat.BINARY:
            # For binary format, look for metadata file
            metadata_path = self.maps_directory / f"{map_name}.meta"
            if metadata_path.exists():
                return metadata_path
        
        extensions = {
            MapDataFormat.TMX: ['.tmx'],
            MapDataFormat.JSON: ['.json'],
            MapDataFormat.BINARY: ['.bin', '.map', '.meta'],
            MapDataFormat.YAML: ['.yaml', '.yml'],
            MapDataFormat.GTA_MAP: ['.gta', '.map']
        }
        
        for ext in extensions.get(format_type, []):
            map_path = self.maps_directory / f"{map_name}{ext}"
            if map_path.exists():
                return map_path
        
        return None
    
    def _get_chunk_id_for_position(self, position: Vector3) -> str:
        """Get chunk ID for a world position"""
        if not self.current_metadata:
            return "0_0"
        
        chunk_x = int(position.x // self.current_metadata.chunk_size)
        chunk_y = int(position.z // self.current_metadata.chunk_size)  # Z is world Y
        
        return f"{self.current_metadata.map_name}_{chunk_x}_{chunk_y}"
    
    def _get_chunk_position(self, chunk_id: str) -> Tuple[int, int]:
        """Extract chunk coordinates from chunk ID"""
        parts = chunk_id.split('_')
        return (int(parts[-2]), int(parts[-1]))
    
    def _update_chunk_loading(self) -> None:
        """Update which chunks should be loaded based on player position"""
        if not self.current_metadata:
            return
        
        player_chunk_x, player_chunk_y = self._get_chunk_position(self.player_chunk_id)
        
        # Determine chunks to load
        chunks_to_load = set()
        chunks_to_activate = set()
        
        for dx in range(-self.preload_radius, self.preload_radius + 1):
            for dy in range(-self.preload_radius, self.preload_radius + 1):
                chunk_x = player_chunk_x + dx
                chunk_y = player_chunk_y + dy
                chunk_id = f"{self.current_metadata.map_name}_{chunk_x}_{chunk_y}"
                
                # Check if chunk is within world bounds
                if self._is_chunk_in_bounds(chunk_x, chunk_y):
                    chunks_to_load.add(chunk_id)
                    
                    # Chunks close to player should be active
                    distance = abs(dx) + abs(dy)  # Manhattan distance
                    if distance <= 1:
                        chunks_to_activate.add(chunk_id)
        
        # Update active chunks
        self.active_chunks = chunks_to_activate
        
        # Start loading chunks that aren't loaded yet
        current_loading = len(self.loading_futures)
        for chunk_id in chunks_to_load:
            if (chunk_id not in self.loaded_chunks and 
                chunk_id not in self.loading_chunks and
                current_loading < self.max_concurrent_loads):
                
                self._start_chunk_load(chunk_id)
                current_loading += 1
    
    def _is_chunk_in_bounds(self, chunk_x: int, chunk_y: int) -> bool:
        """Check if chunk coordinates are within world bounds"""
        if not self.current_metadata:
            return False
        
        world_bounds = self.current_metadata.world_bounds
        world_chunks_x = math.ceil(world_bounds[2] / self.current_metadata.chunk_size)
        world_chunks_y = math.ceil(world_bounds[3] / self.current_metadata.chunk_size)
        
        return (0 <= chunk_x < world_chunks_x and 0 <= chunk_y < world_chunks_y)
    
    def _start_chunk_load(self, chunk_id: str) -> None:
        """Start loading a chunk in background"""
        if not self.current_metadata:
            return
        
        self.loading_chunks.add(chunk_id)
        loader = self.loaders[self.current_metadata.file_format]
        
        # Submit load task to thread pool
        future = self.executor.submit(self._load_chunk_async, chunk_id, loader)
        self.loading_futures[chunk_id] = future
        
        print(f"⏳ Starting load for chunk: {chunk_id}")
    
    def _load_chunk_async(self, chunk_id: str, loader: MapDataLoader) -> Optional[MapChunk]:
        """Load chunk asynchronously"""
        start_time = time.time()
        
        try:
            chunk = loader.load_chunk(chunk_id, self.current_metadata)
            if chunk:
                chunk.load_time = time.time() - start_time
                chunk.last_access_time = time.time()
        
            return chunk
            
        except Exception as e:
            print(f"❌ Async chunk load failed for {chunk_id}: {e}")
            return None
    
    def _process_loading_futures(self) -> None:
        """Process completed chunk loading futures"""
        completed_futures = []
        
        for chunk_id, future in self.loading_futures.items():
            if future.done():
                completed_futures.append(chunk_id)
                
                try:
                    chunk = future.result()
                    if chunk:
                        self.loaded_chunks[chunk_id] = chunk
                        self.load_times.append(chunk.load_time)
                        self.cache_misses += 1
                        print(f"✅ Chunk loaded: {chunk_id} ({chunk.load_time:.3f}s)")
                    else:
                        print(f"❌ Chunk load failed: {chunk_id}")
                        
                except Exception as e:
                    print(f"❌ Error processing chunk load {chunk_id}: {e}")
                
                self.loading_chunks.discard(chunk_id)
        
        # Clean up completed futures
        for chunk_id in completed_futures:
            del self.loading_futures[chunk_id]
    
    def _unload_distant_chunks(self) -> None:
        """Unload chunks that are too far from player"""
        if not self.current_metadata:
            return
        
        player_chunk_x, player_chunk_y = self._get_chunk_position(self.player_chunk_id)
        chunks_to_unload = []
        
        for chunk_id, chunk in self.loaded_chunks.items():
            chunk_x, chunk_y = self._get_chunk_position(chunk_id)
            
            # Calculate distance from player
            distance = max(abs(chunk_x - player_chunk_x), abs(chunk_y - player_chunk_y))
            
            if distance > self.unload_distance:
                chunks_to_unload.append(chunk_id)
        
        # Unload distant chunks
        for chunk_id in chunks_to_unload:
            self._unload_chunk(chunk_id)
            print(f"🗑️ Unloaded distant chunk: {chunk_id}")
        
        # Also limit total loaded chunks
        while len(self.loaded_chunks) > self.max_loaded_chunks:
            # Unload least recently used chunk
            oldest_chunk_id = min(
                self.loaded_chunks.keys(),
                key=lambda cid: self.loaded_chunks[cid].last_access_time
            )
            self._unload_chunk(oldest_chunk_id)
            print(f"🗑️ Unloaded LRU chunk: {oldest_chunk_id}")
    
    def _unload_chunk(self, chunk_id: str) -> None:
        """Unload a specific chunk"""
        if chunk_id in self.loaded_chunks:
            chunk = self.loaded_chunks[chunk_id]
            chunk.state = StreamingState.UNLOADING
            
            # Free memory
            chunk.surface_data = None
            chunk.objects.clear()
            
            del self.loaded_chunks[chunk_id]
        
        self.active_chunks.discard(chunk_id)
    
    def _unload_all_chunks(self) -> None:
        """Unload all chunks"""
        for chunk_id in list(self.loaded_chunks.keys()):
            self._unload_chunk(chunk_id)
        
        # Cancel pending loads
        for future in self.loading_futures.values():
            future.cancel()
        
        self.loading_futures.clear()
        self.loading_chunks.clear()
        self.active_chunks.clear()
    
    def _update_lod_levels(self) -> None:
        """Update Level of Detail for loaded chunks based on distance"""
        if not self.current_metadata:
            return
        
        player_chunk_x, player_chunk_y = self._get_chunk_position(self.player_chunk_id)
        
        for chunk_id, chunk in self.loaded_chunks.items():
            chunk_x, chunk_y = self._get_chunk_position(chunk_id)
            
            # Calculate distance
            distance = max(abs(chunk_x - player_chunk_x), abs(chunk_y - player_chunk_y))
            
            # Assign LOD level
            if distance == 0:
                chunk.lod_level = LODLevel.ULTRA_HIGH
            elif distance == 1:
                chunk.lod_level = LODLevel.HIGH
            elif distance <= 2:
                chunk.lod_level = LODLevel.MEDIUM
            elif distance <= 3:
                chunk.lod_level = LODLevel.LOW
            else:
                chunk.lod_level = LODLevel.VERY_LOW
            
            chunk.last_access_time = time.time()
    
    def get_chunk_at_position(self, position: Vector3) -> Optional[MapChunk]:
        """Get the chunk at a specific world position"""
        chunk_id = self._get_chunk_id_for_position(position)
        chunk = self.loaded_chunks.get(chunk_id)
        
        if chunk:
            chunk.last_access_time = time.time()
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        return chunk
    
    def get_active_chunks(self) -> List[MapChunk]:
        """Get all currently active chunks"""
        active_chunks = []
        for chunk_id in self.active_chunks:
            if chunk_id in self.loaded_chunks:
                active_chunks.append(self.loaded_chunks[chunk_id])
        return active_chunks
    
    def get_streaming_stats(self) -> Dict[str, Any]:
        """Get streaming performance statistics"""
        avg_load_time = sum(self.load_times) / len(self.load_times) if self.load_times else 0.0
        
        return {
            'loaded_chunks': len(self.loaded_chunks),
            'active_chunks': len(self.active_chunks),
            'loading_chunks': len(self.loading_chunks),
            'average_load_time': avg_load_time,
            'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0.0,
            'memory_usage_mb': self.memory_usage / (1024 * 1024),
            'player_chunk': self.player_chunk_id,
            'world_bounds': self.current_metadata.world_bounds if self.current_metadata else None
        }
    
    def create_test_map_data(self, map_name: str) -> None:
        """Create test map data for demonstration"""
        print(f"🏗️ Creating test map data: {map_name}")
        
        # Create metadata
        metadata = MapMetadata(
            map_name=map_name,
            world_bounds=(0, 0, 4096, 4096),  # 4k x 4k world
            chunk_size=512,
            total_chunks=64,  # 8x8 grid
            file_format=MapDataFormat.BINARY,
            preload_radius=2,
            unload_distance=4
        )
        
        # Save metadata
        loader = self.loaders[MapDataFormat.BINARY]
        metadata_path = self.maps_directory / f"{map_name}.meta"
        
        try:
            with metadata_path.open('wb') as f:
                pickle.dump(metadata, f)
            
            # Create some sample chunks
            for chunk_x in range(8):
                for chunk_y in range(8):
                    chunk_id = f"{map_name}_{chunk_x}_{chunk_y}"
                    
                    x = chunk_x * 512
                    y = chunk_y * 512
                    bounds = (x, y, 512, 512)
                    center = Vector3(x + 256, 0, y + 256)
                    
                    chunk = MapChunk(
                        chunk_id=chunk_id,
                        bounds=bounds,
                        center=center,
                        lod_level=LODLevel.LOW
                    )
                    
                    # Add some demo tile data
                    chunk.tile_layers["ground"] = self._generate_test_tiles(bounds)
                    chunk.memory_usage = 1024 * 50  # Estimate 50KB per chunk
                    
                    loader.save_chunk(chunk, metadata)
            
            print(f"✅ Test map created: {map_name} (8x8 chunks)")
            
        except Exception as e:
            print(f"❌ Failed to create test map: {e}")
    
    def _generate_test_tiles(self, bounds: Tuple[int, int, int, int]) -> Dict[str, Any]:
        """Generate test tile data"""
        x, y, w, h = bounds
        tiles = {}
        
        # Create a varied pattern for testing
        for tile_y in range(0, h, 32):
            for tile_x in range(0, w, 32):
                world_x = x + tile_x
                world_y = y + tile_y
                
                # Different patterns for variety
                if (world_x + world_y) % 256 < 64:
                    tiles[(tile_x, tile_y)] = "water"
                elif (world_x // 32) % 10 == 0 or (world_y // 32) % 10 == 0:
                    tiles[(tile_x, tile_y)] = "road"
                elif (world_x // 64) % 5 == 0 and (world_y // 64) % 5 == 0:
                    tiles[(tile_x, tile_y)] = "building"
                else:
                    tiles[(tile_x, tile_y)] = "grass"
        
        return tiles
    
    def shutdown(self) -> None:
        """Shutdown the streaming manager"""
        print("🛑 Shutting down map streaming manager...")
        
        # Cancel all pending operations
        for future in self.loading_futures.values():
            future.cancel()
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        
        # Unload all chunks
        self._unload_all_chunks()
        
        print("✅ Map streaming manager shut down")