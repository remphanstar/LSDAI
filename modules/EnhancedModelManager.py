# Enhanced Model Data Manager with Smart Caching and Discovery
# Save as: modules/EnhancedModelManager.py

import json_utils as js
from CivitaiAPI import CivitAiAPI
from pathlib import Path
import requests
import hashlib
import sqlite3
import pickle
import time
import json
import os
import re

class ModelDatabase:
    """SQLite database for model metadata and caching"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(os.getcwd()) / "data" / "models.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        
    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    style TEXT,
                    base_model TEXT,
                    author TEXT,
                    description TEXT,
                    tags TEXT,
                    url TEXT,
                    download_url TEXT,
                    file_size INTEGER,
                    file_hash TEXT,
                    version TEXT,
                    rating REAL,
                    download_count INTEGER,
                    civitai_id INTEGER,
                    preview_urls TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    downloaded BOOLEAN DEFAULT FALSE,
                    local_path TEXT,
                    verified BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_collections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    models TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_cache (
                    key TEXT PRIMARY KEY,
                    data BLOB,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_models_type ON models(type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_models_style ON models(style)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_models_base ON models(base_model)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_models_rating ON models(rating)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_models_downloaded ON models(downloaded)')
            
    def add_model(self, model_data):
        """Add or update model in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO models 
                (id, name, type, style, base_model, author, description, tags, url, 
                 download_url, file_size, file_hash, version, rating, download_count, 
                 civitai_id, preview_urls, metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                model_data.get('id'),
                model_data.get('name'),
                model_data.get('type'),
                model_data.get('style'),
                model_data.get('base_model'),
                model_data.get('author'),
                model_data.get('description'),
                json.dumps(model_data.get('tags', [])),
                model_data.get('url'),
                model_data.get('download_url'),
                model_data.get('file_size'),
                model_data.get('file_hash'),
                model_data.get('version'),
                model_data.get('rating'),
                model_data.get('download_count'),
                model_data.get('civitai_id'),
                json.dumps(model_data.get('preview_urls', [])),
                json.dumps(model_data.get('metadata', {}))
            ))
            
    def search_models(self, query="", filters=None, limit=100, offset=0):
        """Search models with filters"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            base_query = "SELECT * FROM models WHERE 1=1"
            params = []
            
            if query:
                base_query += " AND (name LIKE ? OR description LIKE ? OR tags LIKE ?)"
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])
                
            if filters:
                if 'type' in filters and filters['type'] != 'all':
                    base_query += " AND type = ?"
                    params.append(filters['type'])
                    
                if 'style' in filters and filters['style'] != 'all':
                    base_query += " AND style = ?"
                    params.append(filters['style'])
                    
                if 'base_model' in filters:
                    base_query += " AND base_model = ?"
                    params.append(filters['base_model'])
                    
                if 'downloaded' in filters:
                    base_query += " AND downloaded = ?"
                    params.append(filters['downloaded'])
                    
                if 'min_rating' in filters:
                    base_query += " AND rating >= ?"
                    params.append(filters['min_rating'])
                    
            base_query += " ORDER BY rating DESC, download_count DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = conn.execute(base_query, params)
            return [dict(row) for row in cursor.fetchall()]
            
    def get_model_stats(self):
        """Get model statistics"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Total models
            cursor = conn.execute("SELECT COUNT(*) FROM models")
            stats['total_models'] = cursor.fetchone()[0]
            
            # Models by type
            cursor = conn.execute("SELECT type, COUNT(*) FROM models GROUP BY type")
            stats['by_type'] = dict(cursor.fetchall())
            
            # Downloaded models
            cursor = conn.execute("SELECT COUNT(*) FROM models WHERE downloaded = 1")
            stats['downloaded'] = cursor.fetchone()[0]
            
            # Total size of downloaded models
            cursor = conn.execute("SELECT SUM(file_size) FROM models WHERE downloaded = 1")
            total_size = cursor.fetchone()[0] or 0
            stats['total_size_gb'] = total_size / (1024**3)
            
            return stats

class SmartModelDiscovery:
    """Smart model discovery using multiple sources"""
    
    def __init__(self, civitai_api=None):
        self.civitai_api = civitai_api
        self.discovery_sources = [
            self._discover_civitai_trending,
            self._discover_civitai_newest,
            self._discover_huggingface_models,
            self._discover_github_repos
        ]
        
    def discover_models(self, categories=None, limit_per_source=20):
        """Discover new models from multiple sources"""
        discovered = []
        
        for source_func in self.discovery_sources:
            try:
                models = source_func(categories, limit_per_source)
                discovered.extend(models)
            except Exception as e:
                print(f"Discovery source error: {e}")
                
        return self._deduplicate_models(discovered)
        
    def _discover_civitai_trending(self, categories=None, limit=20):
        """Discover trending models from CivitAI"""
        if not self.civitai_api:
            return []
            
        try:
            models = self.civitai_api.get_trending_models(limit=limit)
            return self._format_civitai_models(models)
        except Exception as e:
            print(f"CivitAI trending discovery error: {e}")
            return []
            
    def _discover_civitai_newest(self, categories=None, limit=20):
        """Discover newest models from CivitAI"""
        if not self.civitai_api:
            return []
            
        try:
            models = self.civitai_api.get_newest_models(limit=limit)
            return self._format_civitai_models(models)
        except Exception as e:
            print(f"CivitAI newest discovery error: {e}")
            return []
            
    def _discover_huggingface_models(self, categories=None, limit=20):
        """Discover models from Hugging Face"""
        try:
            url = "https://huggingface.co/api/models"
            params = {
                'filter': 'diffusers',
                'sort': 'downloads',
                'direction': '-1',
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._format_huggingface_models(data)
        except Exception as e:
            print(f"Hugging Face discovery error: {e}")
            
        return []
        
    def _discover_github_repos(self, categories=None, limit=20):
        """Discover models from GitHub repositories"""
        try:
            # Search for Stable Diffusion model repositories
            url = "https://api.github.com/search/repositories"
            params = {
                'q': 'stable diffusion models',
                'sort': 'stars',
                'order': 'desc',
                'per_page': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._format_github_repos(data.get('items', []))
        except Exception as e:
            print(f"GitHub discovery error: {e}")
            
        return []
        
    def _format_civitai_models(self, models):
        """Format CivitAI models to standard format"""
        formatted = []
        for model in models:
            formatted.append({
                'id': f"civitai_{model.get('id')}",
                'name': model.get('name'),
                'type': self._map_civitai_type(model.get('type')),
                'author': model.get('creator', {}).get('username'),
                'description': model.get('description'),
                'tags': model.get('tags', []),
                'rating': model.get('stats', {}).get('rating'),
                'download_count': model.get('stats', {}).get('downloadCount'),
                'civitai_id': model.get('id'),
                'url': f"https://civitai.com/models/{model.get('id')}",
                'preview_urls': [img.get('url') for img in model.get('modelVersions', [{}])[0].get('images', [])],
                'source': 'civitai'
            })
        return formatted
        
    def _map_civitai_type(self, civitai_type):
        """Map CivitAI model types to standard types"""
        type_map = {
            'Checkpoint': 'checkpoint',
            'LORA': 'lora',
            'TextualInversion': 'embedding',
            'Hypernetwork': 'hypernetwork',
            'AestheticGradient': 'aesthetic',
            'VAE': 'vae',
            'Poses': 'poses',
            'Controlnet': 'controlnet'
        }
        return type_map.get(civitai_type, 'other')
        
    def _deduplicate_models(self, models):
        """Remove duplicate models based on name and similarity"""
        seen = set()
        deduplicated = []
        
        for model in models:
            # Create a simple fingerprint based on name
            fingerprint = model['name'].lower().strip()
            fingerprint = re.sub(r'[^\w\s]', '', fingerprint)
            
            if fingerprint not in seen:
                seen.add(fingerprint)
                deduplicated.append(model)
                
        return deduplicated

class EnhancedModelManager:
    """Enhanced model manager with smart caching and discovery"""
    
    def __init__(self):
        self.db = ModelDatabase()
        self.civitai_api = self._init_civitai_api()
        self.discovery = SmartModelDiscovery(self.civitai_api)
        self.cache = ModelCache()
        self.collections = ModelCollections(self.db)
        
    def _init_civitai_api(self):
        """Initialize CivitAI API if token available"""
        try:
            settings = js.read(js.SETTINGS_PATH)
            token = settings.get('WIDGETS', {}).get('civitai_token') or os.getenv('CIVITAI_API_TOKEN')
            if token and token != "Set in setup.py":
                return CivitAiAPI(token)
        except Exception as e:
            print(f"CivitAI API initialization error: {e}")
        return None
        
    def search_models(self, query="", filters=None, include_online=True, limit=100):
        """Search models from local database and online sources"""
        # Get local results
        local_results = self.db.search_models(query, filters, limit)
        
        if not include_online:
            return self._format_search_results(local_results, [])
            
        # Get online results if query is not empty
        online_results = []
        if query and len(query) > 2:
            cache_key = f"search_{hashlib.md5(f'{query}_{json.dumps(filters)}'.encode()).hexdigest()}"
            
            cached_results = self.cache.get(cache_key)
            if cached_results:
                online_results = cached_results
            else:
                try:
                    if self.civitai_api:
                        online_results = self.civitai_api.search_models(query, limit=20)
                        self.cache.set(cache_key, online_results, ttl=3600)  # Cache for 1 hour
                except Exception as e:
                    print(f"Online search error: {e}")
                    
        return self._format_search_results(local_results, online_results)
        
    def _format_search_results(self, local_results, online_results):
        """Format and combine search results"""
        # Mark local results
        for result in local_results:
            result['source'] = 'local'
            result['available_offline'] = True
            
        # Mark online results and check if already downloaded
        local_ids = {result['id'] for result in local_results}
        
        for result in online_results:
            result['source'] = 'online'
            result['available_offline'] = result.get('id') in local_ids
            
        # Combine and deduplicate
        all_results = local_results + [r for r in online_results if r.get('id') not in local_ids]
        
        # Sort by relevance (local first, then by rating)
        all_results.sort(key=lambda x: (
            x.get('available_offline', False),
            x.get('rating', 0)
        ), reverse=True)
        
        return all_results
        
    def get_model_recommendations(self, user_preferences=None, limit=10):
        """Get personalized model recommendations"""
        recommendations = []
        
        # Get user's downloaded models to understand preferences
        downloaded_models = self.db.search_models(filters={'downloaded': True})
        
        # Analyze preferences
        preferences = self._analyze_user_preferences(downloaded_models, user_preferences)
        
        # Get recommendations based on preferences
        if preferences:
            # Discover new models similar to user preferences
            discovered = self.discovery.discover_models(
                categories=preferences.get('preferred_types'),
                limit_per_source=limit
            )
            
            # Score and rank recommendations
            scored_recommendations = self._score_recommendations(discovered, preferences)
            recommendations = sorted(scored_recommendations, key=lambda x: x['score'], reverse=True)[:limit]
            
        return recommendations
        
    def _analyze_user_preferences(self, downloaded_models, explicit_preferences=None):
        """Analyze user preferences from downloaded models and explicit settings"""
        if not downloaded_models:
            return explicit_preferences or {}
            
        preferences = {
            'preferred_types': {},
            'preferred_styles': {},
            'preferred_bases': {},
            'average_rating_threshold': 0
        }
        
        # Count model types
        for model in downloaded_models:
            model_type = model.get('type', 'unknown')
            preferences['preferred_types'][model_type] = preferences['preferred_types'].get(model_type, 0) + 1
            
            style = model.get('style')
            if style:
                preferences['preferred_styles'][style] = preferences['preferred_styles'].get(style, 0) + 1
                
            base = model.get('base_model')
            if base:
                preferences['preferred_bases'][base] = preferences['preferred_bases'].get(base, 0) + 1
                
        # Calculate average rating threshold
        ratings = [model.get('rating', 0) for model in downloaded_models if model.get('rating')]
        if ratings:
            preferences['average_rating_threshold'] = sum(ratings) / len(ratings)
            
        # Merge with explicit preferences
        if explicit_preferences:
            preferences.update(explicit_preferences)
            
        return preferences
        
    def _score_recommendations(self, models, preferences):
        """Score model recommendations based on user preferences"""
        scored = []
        
        for model in models:
            score = 0
            
            # Type preference score
            model_type = model.get('type', 'unknown')
            if model_type in preferences.get('preferred_types', {}):
                score += preferences['preferred_types'][model_type] * 0.3
                
            # Style preference score
            style = model.get('style')
            if style and style in preferences.get('preferred_styles', {}):
                score += preferences['preferred_styles'][style] * 0.2
                
            # Rating score
            rating = model.get('rating', 0)
            if rating >= preferences.get('average_rating_threshold', 0):
                score += rating * 0.3
                
            # Popularity score
            downloads = model.get('download_count', 0)
            if downloads > 1000:
                score += min(downloads / 10000, 1.0) * 0.2
                
            model['score'] = score
            scored.append(model)
            
        return scored
        
    def add_model_to_collection(self, collection_name, model_ids):
        """Add models to a collection"""
        return self.collections.add_models(collection_name, model_ids)
        
    def get_collections(self):
        """Get all model collections"""
        return self.collections.get_all()
        
    def sync_downloaded_models(self, models_path):
        """Sync database with actually downloaded models"""
        models_path = Path(models_path)
        if not models_path.exists():
            return
            
        # Scan for model files
        model_extensions = {'.safetensors', '.ckpt', '.pt', '.pth', '.bin'}
        found_models = []
        
        for model_file in models_path.rglob('*'):
            if model_file.suffix.lower() in model_extensions:
                found_models.append(model_file)
                
        # Update database
        for model_file in found_models:
            file_hash = self._calculate_file_hash(model_file)
            
            # Try to find existing model by hash or name
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.execute(
                    "SELECT id FROM models WHERE file_hash = ? OR name LIKE ?",
                    (file_hash, f"%{model_file.stem}%")
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing model
                    conn.execute(
                        "UPDATE models SET downloaded = 1, local_path = ?, file_hash = ? WHERE id = ?",
                        (str(model_file), file_hash, existing[0])
                    )
                else:
                    # Add new model
                    model_id = f"local_{file_hash[:8]}"
                    self.db.add_model({
                        'id': model_id,
                        'name': model_file.stem,
                        'type': self._detect_model_type(model_file),
                        'file_hash': file_hash,
                        'local_path': str(model_file),
                        'downloaded': True
                    })
                    
    def _calculate_file_hash(self, file_path, chunk_size=8192):
        """Calculate file hash for integrity checking"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
        
    def _detect_model_type(self, file_path):
        """Detect model type from file path and name"""
        path_str = str(file_path).lower()
        name = file_path.stem.lower()
        
        if 'lora' in path_str or 'lora' in name:
            return 'lora'
        elif 'vae' in path_str or 'vae' in name:
            return 'vae'
        elif 'controlnet' in path_str or 'controlnet' in name:
            return 'controlnet'
        elif 'embedding' in path_str or 'textual' in path_str:
            return 'embedding'
        else:
            return 'checkpoint'

class ModelCache:
    """Model data caching system"""
    
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            cache_dir = Path(os.getcwd()) / "data" / "cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get(self, key):
        """Get cached data"""
        cache_file = self.cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.cache"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    
                # Check if expired
                if data['expires_at'] > time.time():
                    return data['value']
                else:
                    cache_file.unlink()  # Remove expired cache
            except Exception:
                pass  # Ignore cache read errors
                
        return None
        
    def set(self, key, value, ttl=3600):
        """Set cached data with TTL"""
        cache_file = self.cache_dir / f"{hashlib.md5(key.encode()).hexdigest()}.cache"
        
        data = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Cache write error: {e}")
            
    def clear_expired(self):
        """Clear expired cache entries"""
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    
                if data['expires_at'] <= current_time:
                    cache_file.unlink()
            except Exception:
                cache_file.unlink()  # Remove corrupted cache files

class ModelCollections:
    """Model collections management"""
    
    def __init__(self, database):
        self.db = database
        
    def create_collection(self, name, description="", models=None):
        """Create a new model collection"""
        with sqlite3.connect(self.db.db_path) as conn:
            try:
                conn.execute(
                    "INSERT INTO model_collections (name, description, models) VALUES (?, ?, ?)",
                    (name, description, json.dumps(models or []))
                )
                return True
            except sqlite3.IntegrityError:
                return False  # Collection already exists
                
    def add_models(self, collection_name, model_ids):
        """Add models to collection"""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT models FROM model_collections WHERE name = ?",
                (collection_name,)
            )
            result = cursor.fetchone()
            
            if result:
                current_models = json.loads(result[0])
                current_models.extend(model_ids)
                current_models = list(set(current_models))  # Remove duplicates
                
                conn.execute(
                    "UPDATE model_collections SET models = ? WHERE name = ?",
                    (json.dumps(current_models), collection_name)
                )
                return True
                
        return False
        
    def get_all(self):
        """Get all collections"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM model_collections ORDER BY created_at DESC")
            
            collections = []
            for row in cursor.fetchall():
                collection = dict(row)
                collection['models'] = json.loads(collection['models'])
                collections.append(collection)
                
            return collections

# Global instance
enhanced_model_manager = None

def get_enhanced_model_manager():
    """Get or create enhanced model manager"""
    global enhanced_model_manager
    
    if enhanced_model_manager is None:
        enhanced_model_manager = EnhancedModelManager()
        
    return enhanced_model_manager

print("Enhanced Model Manager loaded with smart caching and discovery!")
