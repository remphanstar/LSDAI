# Advanced Extension Manager with Auto-Updates and Dependencies
# Save as: modules/ExtensionManager.py

import json_utils as js
from pathlib import Path
import subprocess
import threading
import requests
import sqlite3
import hashlib
import zipfile
import shutil
import time
import json
import git
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class ExtensionRepository:
    """Manages extension repository information and metadata"""
    
    def __init__(self):
        self.repositories = self._load_default_repositories()
        self.custom_repos = self._load_custom_repositories()
        self.cache_file = Path('data/extension_cache.json')
        self.cache_ttl = 3600 * 6  # 6 hours
        
    def _load_default_repositories(self):
        """Load default extension repositories"""
        return {
            'a1111_extensions': {
                'name': 'Automatic1111 Extensions',
                'url': 'https://raw.githubusercontent.com/AUTOMATIC1111/stable-diffusion-webui-extensions/master/index.json',
                'type': 'index',
                'enabled': True
            },
            'comfyui_manager': {
                'name': 'ComfyUI Manager',
                'url': 'https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main/extension-node-map.json',
                'type': 'index',
                'enabled': True
            },
            'github_search': {
                'name': 'GitHub Search',
                'url': 'https://api.github.com/search/repositories',
                'type': 'search',
                'enabled': True,
                'search_queries': [
                    'stable-diffusion-webui extension',
                    'comfyui custom nodes',
                    'stable diffusion extension'
                ]
            }
        }
        
    def _load_custom_repositories(self):
        """Load custom user-added repositories"""
        try:
            custom_file = Path('data/custom_repositories.json')
            if custom_file.exists():
                with open(custom_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading custom repositories: {e}")
        return {}
        
    def add_repository(self, name: str, url: str, repo_type: str = 'index'):
        """Add custom repository"""
        self.custom_repos[name] = {
            'name': name,
            'url': url,
            'type': repo_type,
            'enabled': True,
            'added_date': time.time()
        }
        
        # Save to file
        try:
            custom_file = Path('data/custom_repositories.json')
            custom_file.parent.mkdir(exist_ok=True)
            with open(custom_file, 'w') as f:
                json.dump(self.custom_repos, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving custom repository: {e}")
            return False
            
    def fetch_extensions(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Fetch extensions from all repositories"""
        cache_data = self._load_cache()
        
        if not force_refresh and cache_data and self._is_cache_valid(cache_data):
            return cache_data['extensions']
            
        all_extensions = []
        
        # Fetch from default repositories
        for repo_id, repo_info in self.repositories.items():
            if repo_info['enabled']:
                extensions = self._fetch_from_repository(repo_info)
                all_extensions.extend(extensions)
                
        # Fetch from custom repositories
        for repo_id, repo_info in self.custom_repos.items():
            if repo_info['enabled']:
                extensions = self._fetch_from_repository(repo_info)
                all_extensions.extend(extensions)
                
        # Deduplicate and cache
        deduplicated = self._deduplicate_extensions(all_extensions)
        self._save_cache({'extensions': deduplicated, 'timestamp': time.time()})
        
        return deduplicated
        
    def _fetch_from_repository(self, repo_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch extensions from a specific repository"""
        extensions = []
        
        try:
            if repo_info['type'] == 'index':
                extensions = self._fetch_from_index(repo_info['url'])
            elif repo_info['type'] == 'search':
                extensions = self._fetch_from_search(repo_info)
                
        except Exception as e:
            print(f"Error fetching from repository {repo_info['name']}: {e}")
            
        return extensions
        
    def _fetch_from_index(self, url: str) -> List[Dict[str, Any]]:
        """Fetch extensions from index URL"""
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            # Handle different index formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if 'extensions' in data:
                    return data['extensions']
                elif 'custom_nodes' in data:
                    return data['custom_nodes']
                    
        return []
        
    def _fetch_from_search(self, repo_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch extensions using GitHub search"""
        extensions = []
        
        for query in repo_info.get('search_queries', []):
            try:
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 20
                }
                
                response = requests.get(repo_info['url'], params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', []):
                        extension = {
                            'name': item['name'],
                            'description': item['description'],
                            'url': item['clone_url'],
                            'stars': item['stargazers_count'],
                            'updated': item['updated_at'],
                            'author': item['owner']['login'],
                            'source': 'github_search'
                        }
                        extensions.append(extension)
                        
            except Exception as e:
                print(f"Error searching GitHub: {e}")
                
        return extensions
        
    def _deduplicate_extensions(self, extensions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate extensions"""
        seen = set()
        deduplicated = []
        
        for ext in extensions:
            # Use URL or name as identifier
            identifier = ext.get('url', ext.get('name', '')).lower()
            if identifier and identifier not in seen:
                seen.add(identifier)
                deduplicated.append(ext)
                
        return deduplicated
        
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load extension cache"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
        
    def _save_cache(self, data: Dict[str, Any]):
        """Save extension cache"""
        try:
            self.cache_file.parent.mkdir(exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
            
    def _is_cache_valid(self, cache_data: Dict[str, Any]) -> bool:
        """Check if cache is still valid"""
        timestamp = cache_data.get('timestamp', 0)
        return (time.time() - timestamp) < self.cache_ttl

class ExtensionInstaller:
    """Handles extension installation and management"""
    
    def __init__(self, webui_path: Path):
        self.webui_path = Path(webui_path)
        self.extensions_path = self.webui_path / 'extensions'
        self.extensions_path.mkdir(exist_ok=True)
        
    def install_extension(self, extension_info: Dict[str, Any], update_if_exists: bool = False) -> Dict[str, Any]:
        """Install an extension"""
        ext_name = extension_info.get('name', 'unknown')
        ext_url = extension_info.get('url', '')
        
        if not ext_url:
            return {'success': False, 'error': 'No URL provided'}
            
        ext_path = self.extensions_path / ext_name
        
        # Check if extension already exists
        if ext_path.exists():
            if not update_if_exists:
                return {'success': False, 'error': 'Extension already exists'}
            else:
                return self.update_extension(ext_name)
                
        try:
            print(f"📦 Installing extension: {ext_name}")
            
            # Clone the repository
            git.Repo.clone_from(ext_url, ext_path)
            
            # Install dependencies if requirements.txt exists
            req_file = ext_path / 'requirements.txt'
            if req_file.exists():
                self._install_requirements(req_file)
                
            # Run install script if exists
            install_script = ext_path / 'install.py'
            if install_script.exists():
                self._run_install_script(install_script)
                
            return {
                'success': True,
                'message': f'Extension {ext_name} installed successfully',
                'path': str(ext_path)
            }
            
        except Exception as e:
            # Cleanup on failure
            if ext_path.exists():
                shutil.rmtree(ext_path, ignore_errors=True)
                
            return {
                'success': False,
                'error': f'Installation failed: {str(e)}'
            }
            
    def update_extension(self, extension_name: str) -> Dict[str, Any]:
        """Update an existing extension"""
        ext_path = self.extensions_path / extension_name
        
        if not ext_path.exists():
            return {'success': False, 'error': 'Extension not found'}
            
        try:
            print(f"🔄 Updating extension: {extension_name}")
            
            repo = git.Repo(ext_path)
            
            # Get current commit
            old_commit = repo.head.commit.hexsha
            
            # Pull latest changes
            repo.remotes.origin.pull()
            
            new_commit = repo.head.commit.hexsha
            
            # Check if there were updates
            if old_commit == new_commit:
                return {
                    'success': True,
                    'message': 'Extension is already up to date',
                    'updated': False
                }
            else:
                # Update dependencies if needed
                req_file = ext_path / 'requirements.txt'
                if req_file.exists():
                    self._install_requirements(req_file)
                    
                return {
                    'success': True,
                    'message': f'Extension {extension_name} updated successfully',
                    'updated': True,
                    'old_commit': old_commit[:8],
                    'new_commit': new_commit[:8]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Update failed: {str(e)}'
            }
            
    def uninstall_extension(self, extension_name: str) -> Dict[str, Any]:
        """Uninstall an extension"""
        ext_path = self.extensions_path / extension_name
        
        if not ext_path.exists():
            return {'success': False, 'error': 'Extension not found'}
            
        try:
            print(f"🗑️ Uninstalling extension: {extension_name}")
            
            # Run uninstall script if exists
            uninstall_script = ext_path / 'uninstall.py'
            if uninstall_script.exists():
                self._run_uninstall_script(uninstall_script)
                
            # Remove directory
            shutil.rmtree(ext_path)
            
            return {
                'success': True,
                'message': f'Extension {extension_name} uninstalled successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Uninstall failed: {str(e)}'
            }
            
    def get_installed_extensions(self) -> List[Dict[str, Any]]:
        """Get list of installed extensions"""
        extensions = []
        
        for ext_dir in self.extensions_path.iterdir():
            if ext_dir.is_dir() and not ext_dir.name.startswith('.'):
                ext_info = self._get_extension_info(ext_dir)
                extensions.append(ext_info)
                
        return extensions
        
    def _get_extension_info(self, ext_path: Path) -> Dict[str, Any]:
        """Get information about an installed extension"""
        info = {
            'name': ext_path.name,
            'path': str(ext_path),
            'installed': True
        }
        
        try:
            # Try to get git information
            repo = git.Repo(ext_path)
            info.update({
                'git_url': repo.remotes.origin.url,
                'current_commit': repo.head.commit.hexsha,
                'current_branch': repo.active_branch.name,
                'last_update': repo.head.commit.committed_datetime.isoformat()
            })
            
            # Check for updates
            try:
                repo.remotes.origin.fetch()
                commits_behind = list(repo.iter_commits('HEAD..origin/HEAD'))
                info['updates_available'] = len(commits_behind) > 0
                info['commits_behind'] = len(commits_behind)
            except Exception:
                info['updates_available'] = False
                
        except Exception:
            info['git_url'] = None
            
        # Check for metadata files
        metadata_files = ['extension.json', 'package.json', 'setup.py']
        for meta_file in metadata_files:
            meta_path = ext_path / meta_file
            if meta_path.exists():
                try:
                    if meta_file.endswith('.json'):
                        with open(meta_path, 'r') as f:
                            metadata = json.load(f)
                            info.update(metadata)
                except Exception:
                    pass
                    
        return info
        
    def _install_requirements(self, req_file: Path):
        """Install Python requirements"""
        try:
            subprocess.run([
                'pip', 'install', '-r', str(req_file)
            ], check=True, capture_output=True)
            print(f"✅ Installed requirements from {req_file}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Failed to install requirements: {e}")
            
    def _run_install_script(self, script_path: Path):
        """Run extension install script"""
        try:
            subprocess.run([
                'python', str(script_path)
            ], check=True, capture_output=True, cwd=script_path.parent)
            print(f"✅ Ran install script: {script_path}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Install script failed: {e}")
            
    def _run_uninstall_script(self, script_path: Path):
        """Run extension uninstall script"""
        try:
            subprocess.run([
                'python', str(script_path)
            ], check=True, capture_output=True, cwd=script_path.parent)
            print(f"✅ Ran uninstall script: {script_path}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Uninstall script failed: {e}")

class ExtensionManager:
    """Main extension manager class"""
    
    def __init__(self, webui_path: Path = None):
        if webui_path is None:
            webui_path = Path(os.getcwd()) / 'stable-diffusion-webui'
            
        self.webui_path = Path(webui_path)
        self.repository = ExtensionRepository()
        self.installer = ExtensionInstaller(self.webui_path)
        self.db_path = Path('data/extensions.db')
        self._init_database()
        
    def _init_database(self):
        """Initialize extension management database"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS extensions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT,
                    description TEXT,
                    author TEXT,
                    version TEXT,
                    installed BOOLEAN DEFAULT FALSE,
                    enabled BOOLEAN DEFAULT TRUE,
                    install_date REAL,
                    last_update REAL,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS extension_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    extension_name TEXT NOT NULL,
                    old_version TEXT,
                    new_version TEXT,
                    update_date REAL,
                    success BOOLEAN,
                    notes TEXT
                )
            ''')
            
    def search_extensions(self, query: str = "", category: str = None, 
                         installed_only: bool = False) -> List[Dict[str, Any]]:
        """Search for extensions"""
        if installed_only:
            extensions = self.installer.get_installed_extensions()
        else:
            extensions = self.repository.fetch_extensions()
            
        if query:
            query = query.lower()
            extensions = [
                ext for ext in extensions
                if query in ext.get('name', '').lower() or 
                   query in ext.get('description', '').lower()
            ]
            
        if category:
            extensions = [
                ext for ext in extensions
                if ext.get('category') == category
            ]
            
        return extensions
        
    def install_extension(self, extension_info: Dict[str, Any]) -> Dict[str, Any]:
        """Install extension and track in database"""
        result = self.installer.install_extension(extension_info)
        
        if result['success']:
            # Record in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO extensions 
                    (name, url, description, author, installed, install_date, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    extension_info.get('name'),
                    extension_info.get('url'),
                    extension_info.get('description'),
                    extension_info.get('author'),
                    True,
                    time.time(),
                    json.dumps(extension_info)
                ))
                
        return result
        
    def batch_install_extensions(self, extension_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Install multiple extensions"""
        results = {
            'successful': [],
            'failed': [],
            'total': len(extension_list)
        }
        
        for ext_info in extension_list:
            print(f"📦 Installing {ext_info.get('name', 'unknown')}...")
            result = self.install_extension(ext_info)
            
            if result['success']:
                results['successful'].append(ext_info['name'])
            else:
                results['failed'].append({
                    'name': ext_info['name'],
                    'error': result['error']
                })
                
        return results
        
    def update_all_extensions(self) -> Dict[str, Any]:
        """Update all installed extensions"""
        installed = self.installer.get_installed_extensions()
        results = {
            'updated': [],
            'up_to_date': [],
            'failed': [],
            'total': len(installed)
        }
        
        for ext in installed:
            if ext.get('updates_available', False):
                print(f"🔄 Updating {ext['name']}...")
                result = self.installer.update_extension(ext['name'])
                
                if result['success']:
                    if result.get('updated', False):
                        results['updated'].append(ext['name'])
                        
                        # Record update in database
                        with sqlite3.connect(self.db_path) as conn:
                            conn.execute('''
                                INSERT INTO extension_updates 
                                (extension_name, old_version, new_version, update_date, success)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (
                                ext['name'],
                                result.get('old_commit', ''),
                                result.get('new_commit', ''),
                                time.time(),
                                True
                            ))
                    else:
                        results['up_to_date'].append(ext['name'])
                else:
                    results['failed'].append({
                        'name': ext['name'],
                        'error': result['error']
                    })
            else:
                results['up_to_date'].append(ext['name'])
                
        return results
        
    def get_extension_recommendations(self, user_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get extension recommendations based on user preferences"""
        all_extensions = self.repository.fetch_extensions()
        installed_extensions = {ext['name'] for ext in self.installer.get_installed_extensions()}
        
        # Filter out already installed
        available_extensions = [
            ext for ext in all_extensions 
            if ext.get('name') not in installed_extensions
        ]
        
        # Score extensions based on popularity and relevance
        scored_extensions = []
        for ext in available_extensions:
            score = 0
            
            # Popularity score
            stars = ext.get('stars', 0)
            if stars > 100:
                score += min(stars / 1000, 5)
                
            # Recent activity score
            updated = ext.get('updated', '')
            if updated:
                try:
                    update_time = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    days_since_update = (datetime.now(update_time.tzinfo) - update_time).days
                    if days_since_update < 30:
                        score += 2
                    elif days_since_update < 90:
                        score += 1
                except Exception:
                    pass
                    
            # Category preferences
            if user_preferences:
                preferred_categories = user_preferences.get('categories', [])
                ext_category = ext.get('category', '')
                if ext_category in preferred_categories:
                    score += 3
                    
            ext['recommendation_score'] = score
            scored_extensions.append(ext)
            
        # Sort by score and return top recommendations
        scored_extensions.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return scored_extensions[:20]
        
    def create_extension_backup(self, output_path: str = None) -> Dict[str, Any]:
        """Create backup of all installed extensions"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"extension_backup_{timestamp}.json"
            
        installed = self.installer.get_installed_extensions()
        
        backup_data = {
            'backup_date': time.time(),
            'webui_path': str(self.webui_path),
            'extensions': []
        }
        
        for ext in installed:
            ext_backup = {
                'name': ext['name'],
                'url': ext.get('git_url'),
                'commit': ext.get('current_commit'),
                'branch': ext.get('current_branch'),
                'metadata': ext
            }
            backup_data['extensions'].append(ext_backup)
            
        try:
            with open(output_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
                
            return {
                'success': True,
                'backup_file': output_path,
                'extensions_count': len(installed)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def restore_from_backup(self, backup_file: str) -> Dict[str, Any]:
        """Restore extensions from backup"""
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
                
            extensions_to_install = backup_data.get('extensions', [])
            
            # Convert backup format to installation format
            install_list = []
            for ext in extensions_to_install:
                if ext.get('url'):
                    install_list.append({
                        'name': ext['name'],
                        'url': ext['url']
                    })
                    
            return self.batch_install_extensions(install_list)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Backup restore failed: {str(e)}'
            }
            
    def get_extension_statistics(self) -> Dict[str, Any]:
        """Get extension usage statistics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Total extensions
            cursor = conn.execute("SELECT COUNT(*) as total FROM extensions WHERE installed = 1")
            total_installed = cursor.fetchone()['total']
            
            # Recent installs
            week_ago = time.time() - (7 * 24 * 3600)
            cursor = conn.execute(
                "SELECT COUNT(*) as recent FROM extensions WHERE install_date > ?",
                (week_ago,)
            )
            recent_installs = cursor.fetchone()['recent']
            
            # Update history
            cursor = conn.execute("SELECT COUNT(*) as updates FROM extension_updates")
            total_updates = cursor.fetchone()['updates']
            
            return {
                'total_installed': total_installed,
                'recent_installs': recent_installs,
                'total_updates': total_updates,
                'webui_path': str(self.webui_path)
            }

# Global extension manager instance
extension_manager = None

def get_extension_manager():
    """Get or create extension manager instance"""
    global extension_manager
    
    if extension_manager is None:
        extension_manager = ExtensionManager()
        
    return extension_manager

def install_recommended_extensions():
    """Install a curated list of recommended extensions"""
    manager = get_extension_manager()
    
    recommended = [
        {
            'name': 'sd-webui-controlnet',
            'url': 'https://github.com/Mikubill/sd-webui-controlnet.git'
        },
        {
            'name': 'stable-diffusion-webui-images-browser',
            'url': 'https://github.com/AlUlkesh/stable-diffusion-webui-images-browser.git'
        },
        {
            'name': 'sd-dynamic-thresholding',
            'url': 'https://github.com/mcmonkeyprojects/sd-dynamic-thresholding.git'
        }
    ]
    
    return manager.batch_install_extensions(recommended)

def auto_update_extensions():
    """Auto-update all extensions (can be called periodically)"""
    manager = get_extension_manager()
    return manager.update_all_extensions()

print("Advanced Extension Manager with Auto-Updates loaded!")
