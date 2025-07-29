# Cloud Sync and Backup System for LSDAI
# Save as: modules/CloudSync.py

import json_utils as js
from pathlib import Path
import subprocess
import threading
import requests
import zipfile
import hashlib
import base64
import time
import json
import os
import io
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3

class GoogleDriveSync:
    """Google Drive synchronization for settings and models"""
    
    def __init__(self, credentials_file: str = None):
        self.credentials_file = credentials_file
        self.drive_service = None
        self.sync_folder_id = None
        self.sync_enabled = False
        
    def authenticate(self, credentials_json: str = None) -> bool:
        """Authenticate with Google Drive"""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import Flow
            from googleapiclient.discovery import build
            
            if credentials_json:
                # Use provided credentials
                creds_data = json.loads(credentials_json)
                credentials = Credentials.from_authorized_user_info(creds_data)
            elif self.credentials_file and Path(self.credentials_file).exists():
                # Load from file
                with open(self.credentials_file, 'r') as f:
                    creds_data = json.load(f)
                credentials = Credentials.from_authorized_user_info(creds_data)
            else:
                return False
                
            self.drive_service = build('drive', 'v3', credentials=credentials)
            self.sync_enabled = True
            
            # Create or find sync folder
            self._setup_sync_folder()
            
            return True
            
        except Exception as e:
            print(f"Google Drive authentication failed: {e}")
            return False
            
    def _setup_sync_folder(self):
        """Create or find the LSDAI sync folder"""
        try:
            # Search for existing folder
            query = "name='LSDAI_Sync' and mimeType='application/vnd.google-apps.folder'"
            results = self.drive_service.files().list(q=query).execute()
            
            if results['files']:
                self.sync_folder_id = results['files'][0]['id']
            else:
                # Create new folder
                folder_metadata = {
                    'name': 'LSDAI_Sync',
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.drive_service.files().create(body=folder_metadata).execute()
                self.sync_folder_id = folder['id']
                
        except Exception as e:
            print(f"Error setting up sync folder: {e}")
            
    def upload_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Upload settings to Google Drive"""
        if not self.sync_enabled:
            return False
            
        try:
            timestamp = datetime.now().isoformat()
            filename = f"lsdai_settings_{timestamp}.json"
            
            # Prepare file content
            content = json.dumps(settings_data, indent=2)
            media_body = io.StringIO(content)
            
            file_metadata = {
                'name': filename,
                'parents': [self.sync_folder_id]
            }
            
            # Upload file
            self.drive_service.files().create(
                body=file_metadata,
                media_body=media_body,
                media_mime_type='application/json'
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Settings upload failed: {e}")
            return False
            
    def download_latest_settings(self) -> Optional[Dict[str, Any]]:
        """Download latest settings from Google Drive"""
        if not self.sync_enabled:
            return None
            
        try:
            # Find latest settings file
            query = f"name contains 'lsdai_settings' and parents in '{self.sync_folder_id}'"
            results = self.drive_service.files().list(
                q=query,
                orderBy='modifiedTime desc',
                pageSize=1
            ).execute()
            
            if not results['files']:
                return None
                
            file_id = results['files'][0]['id']
            
            # Download file content
            content = self.drive_service.files().get_media(fileId=file_id).execute()
            settings_data = json.loads(content.decode('utf-8'))
            
            return settings_data
            
        except Exception as e:
            print(f"Settings download failed: {e}")
            return None
            
    def sync_model_list(self, model_list: List[Dict[str, Any]]) -> bool:
        """Sync model list to cloud"""
        if not self.sync_enabled:
            return False
            
        try:
            sync_data = {
                'timestamp': time.time(),
                'model_count': len(model_list),
                'models': model_list
            }
            
            content = json.dumps(sync_data, indent=2)
            media_body = io.StringIO(content)
            
            # Check if model list file exists
            query = f"name='model_list.json' and parents in '{self.sync_folder_id}'"
            results = self.drive_service.files().list(q=query).execute()
            
            if results['files']:
                # Update existing file
                file_id = results['files'][0]['id']
                self.drive_service.files().update(
                    fileId=file_id,
                    media_body=media_body,
                    media_mime_type='application/json'
                ).execute()
            else:
                # Create new file
                file_metadata = {
                    'name': 'model_list.json',
                    'parents': [self.sync_folder_id]
                }
                self.drive_service.files().create(
                    body=file_metadata,
                    media_body=media_body,
                    media_mime_type='application/json'
                ).execute()
                
            return True
            
        except Exception as e:
            print(f"Model list sync failed: {e}")
            return False

class GitHubBackup:
    """GitHub-based backup system using private repositories"""
    
    def __init__(self, token: str = None, repo_name: str = "lsdai-backup"):
        self.token = token
        self.repo_name = repo_name
        self.api_base = "https://api.github.com"
        self.repo_full_name = None
        
    def authenticate(self, token: str) -> bool:
        """Set GitHub token and validate"""
        self.token = token
        
        try:
            headers = {'Authorization': f'token {token}'}
            response = requests.get(f"{self.api_base}/user", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                self.username = user_data['login']
                self.repo_full_name = f"{self.username}/{self.repo_name}"
                return True
                
        except Exception as e:
            print(f"GitHub authentication failed: {e}")
            
        return False
        
    def create_backup_repo(self) -> bool:
        """Create private backup repository"""
        if not self.token:
            return False
            
        try:
            headers = {
                'Authorization': f'token {self.token}',
                'Content-Type': 'application/json'
            }
            
            repo_data = {
                'name': self.repo_name,
                'description': 'LSDAI Settings and Configuration Backup',
                'private': True,
                'auto_init': True
            }
            
            response = requests.post(
                f"{self.api_base}/user/repos",
                headers=headers,
                json=repo_data
            )
            
            return response.status_code == 201
            
        except Exception as e:
            print(f"Backup repo creation failed: {e}")
            return False
            
    def backup_settings(self, settings_data: Dict[str, Any], commit_message: str = None) -> bool:
        """Backup settings to GitHub repository"""
        if not self.token or not self.repo_full_name:
            return False
            
        try:
            headers = {
                'Authorization': f'token {self.token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare file content
            content = json.dumps(settings_data, indent=2)
            content_b64 = base64.b64encode(content.encode()).decode()
            
            filename = f"settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            if commit_message is None:
                commit_message = f"Backup settings - {datetime.now().isoformat()}"
                
            # Check if file exists to get SHA
            file_url = f"{self.api_base}/repos/{self.repo_full_name}/contents/{filename}"
            
            file_data = {
                'message': commit_message,
                'content': content_b64
            }
            
            response = requests.put(file_url, headers=headers, json=file_data)
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"GitHub backup failed: {e}")
            return False
            
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups"""
        if not self.token or not self.repo_full_name:
            return []
            
        try:
            headers = {'Authorization': f'token {self.token}'}
            
            response = requests.get(
                f"{self.api_base}/repos/{self.repo_full_name}/contents",
                headers=headers
            )
            
            if response.status_code == 200:
                files = response.json()
                backups = []
                
                for file_info in files:
                    if file_info['name'].startswith('settings_') and file_info['name'].endswith('.json'):
                        backups.append({
                            'name': file_info['name'],
                            'size': file_info['size'],
                            'download_url': file_info['download_url'],
                            'sha': file_info['sha']
                        })
                        
                return sorted(backups, key=lambda x: x['name'], reverse=True)
                
        except Exception as e:
            print(f"Error listing backups: {e}")
            
        return []
        
    def restore_backup(self, backup_name: str) -> Optional[Dict[str, Any]]:
        """Restore settings from backup"""
        backups = self.list_backups()
        backup_info = next((b for b in backups if b['name'] == backup_name), None)
        
        if not backup_info:
            return None
            
        try:
            response = requests.get(backup_info['download_url'])
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            print(f"Backup restore failed: {e}")
            
        return None

class CloudSyncManager:
    """Main cloud sync manager coordinating different services"""
    
    def __init__(self):
        self.gdrive_sync = GoogleDriveSync()
        self.github_backup = GitHubBackup()
        self.sync_db = self._init_sync_database()
        self.auto_sync_enabled = False
        self.sync_interval = 3600  # 1 hour
        self.sync_thread = None
        
    def _init_sync_database(self):
        """Initialize sync tracking database"""
        db_path = Path('data/cloud_sync.db')
        db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sync_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    service TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    details TEXT,
                    file_size INTEGER
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sync_config (
                    service TEXT PRIMARY KEY,
                    enabled BOOLEAN DEFAULT FALSE,
                    last_sync REAL,
                    config_data TEXT
                )
            ''')
            
        return db_path
        
    def configure_google_drive(self, credentials_json: str) -> bool:
        """Configure Google Drive sync"""
        success = self.gdrive_sync.authenticate(credentials_json)
        
        if success:
            self._update_sync_config('google_drive', {
                'enabled': True,
                'configured_at': time.time()
            })
            
        return success
        
    def configure_github_backup(self, token: str, repo_name: str = "lsdai-backup") -> bool:
        """Configure GitHub backup"""
        self.github_backup.repo_name = repo_name
        success = self.github_backup.authenticate(token)
        
        if success:
            # Try to create backup repo if it doesn't exist
            self.github_backup.create_backup_repo()
            
            self._update_sync_config('github', {
                'enabled': True,
                'token': token,  # Store encrypted in real implementation
                'repo_name': repo_name,
                'configured_at': time.time()
            })
            
        return success
        
    def sync_all_data(self, force: bool = False) -> Dict[str, Any]:
        """Sync all data to configured cloud services"""
        results = {
            'google_drive': {'attempted': False, 'success': False},
            'github': {'attempted': False, 'success': False},
            'timestamp': time.time()
        }
        
        # Gather all data to sync
        sync_data = self._gather_sync_data()
        
        # Sync to Google Drive
        if self.gdrive_sync.sync_enabled:
            results['google_drive']['attempted'] = True
            try:
                success = self.gdrive_sync.upload_settings(sync_data)
                results['google_drive']['success'] = success
                
                self._record_sync_operation('google_drive', 'upload', success, sync_data)
                
            except Exception as e:
                results['google_drive']['error'] = str(e)
                
        # Backup to GitHub
        if self.github_backup.token:
            results['github']['attempted'] = True
            try:
                success = self.github_backup.backup_settings(sync_data)
                results['github']['success'] = success
                
                self._record_sync_operation('github', 'backup', success, sync_data)
                
            except Exception as e:
                results['github']['error'] = str(e)
                
        return results
        
    def _gather_sync_data(self) -> Dict[str, Any]:
        """Gather all data that should be synced"""
        sync_data = {
            'sync_timestamp': time.time(),
            'lsdai_version': '2.0.0',  # Update with actual version
            'settings': {},
            'model_favorites': [],
            'extension_list': [],
            'custom_configs': {}
        }
        
        try:
            # Load main settings
            settings = js.read(js.SETTINGS_PATH)
            sync_data['settings'] = settings
            
            # Load model favorites
            favorites_file = Path('data/model_favorites.json')
            if favorites_file.exists():
                with open(favorites_file, 'r') as f:
                    sync_data['model_favorites'] = json.load(f)
                    
            # Load extension configuration
            from modules.ExtensionManager import get_extension_manager
            ext_manager = get_extension_manager()
            sync_data['extension_list'] = ext_manager.get_extension_statistics()
            
            # Load custom configurations
            custom_config_dir = Path('data/custom_configs')
            if custom_config_dir.exists():
                for config_file in custom_config_dir.glob('*.json'):
                    with open(config_file, 'r') as f:
                        sync_data['custom_configs'][config_file.stem] = json.load(f)
                        
        except Exception as e:
            print(f"Error gathering sync data: {e}")
            
        return sync_data
        
    def restore_from_cloud(self, service: str = 'auto') -> Dict[str, Any]:
        """Restore data from cloud service"""
        if service == 'auto':
            # Try Google Drive first, then GitHub
            for svc in ['google_drive', 'github']:
                result = self.restore_from_cloud(svc)
                if result['success']:
                    return result
            return {'success': False, 'error': 'No valid backup found'}
            
        if service == 'google_drive' and self.gdrive_sync.sync_enabled:
            try:
                data = self.gdrive_sync.download_latest_settings()
                if data:
                    self._apply_restored_data(data)
                    return {'success': True, 'service': 'google_drive', 'data': data}
            except Exception as e:
                return {'success': False, 'error': str(e)}
                
        elif service == 'github' and self.github_backup.token:
            try:
                backups = self.github_backup.list_backups()
                if backups:
                    latest_backup = backups[0]
                    data = self.github_backup.restore_backup(latest_backup['name'])
                    if data:
                        self._apply_restored_data(data)
                        return {'success': True, 'service': 'github', 'data': data}
            except Exception as e:
                return {'success': False, 'error': str(e)}
                
        return {'success': False, 'error': f'Service {service} not available'}
        
    def _apply_restored_data(self, data: Dict[str, Any]):
        """Apply restored data to local system"""
        try:
            # Restore main settings
            if 'settings' in data:
                js.write(js.SETTINGS_PATH, data['settings'])
                
            # Restore model favorites
            if 'model_favorites' in data:
                favorites_file = Path('data/model_favorites.json')
                favorites_file.parent.mkdir(exist_ok=True)
                with open(favorites_file, 'w') as f:
                    json.dump(data['model_favorites'], f, indent=2)
                    
            # Restore custom configs
            if 'custom_configs' in data:
                custom_config_dir = Path('data/custom_configs')
                custom_config_dir.mkdir(exist_ok=True)
                
                for config_name, config_data in data['custom_configs'].items():
                    config_file = custom_config_dir / f"{config_name}.json"
                    with open(config_file, 'w') as f:
                        json.dump(config_data, f, indent=2)
                        
            print("✅ Data restored successfully")
            
        except Exception as e:
            print(f"❌ Error applying restored data: {e}")
            
    def start_auto_sync(self, interval: int = 3600):
        """Start automatic synchronization"""
        self.auto_sync_enabled = True
        self.sync_interval = interval
        
        def sync_loop():
            while self.auto_sync_enabled:
                time.sleep(self.sync_interval)
                if self.auto_sync_enabled:
                    print("🔄 Auto-sync: Starting scheduled sync...")
                    result = self.sync_all_data()
                    print(f"🔄 Auto-sync completed: {result}")
                    
        self.sync_thread = threading.Thread(target=sync_loop, daemon=True)
        self.sync_thread.start()
        
        print(f"🔄 Auto-sync started (interval: {interval}s)")
        
    def stop_auto_sync(self):
        """Stop automatic synchronization"""
        self.auto_sync_enabled = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        print("🔄 Auto-sync stopped")
        
    def _update_sync_config(self, service: str, config: Dict[str, Any]):
        """Update sync configuration in database"""
        with sqlite3.connect(self.sync_db) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO sync_config (service, enabled, config_data)
                VALUES (?, ?, ?)
            ''', (service, config.get('enabled', False), json.dumps(config)))
            
    def _record_sync_operation(self, service: str, operation: str, success: bool, data: Dict[str, Any]):
        """Record sync operation in database"""
        data_size = len(json.dumps(data).encode('utf-8'))
        
        with sqlite3.connect(self.sync_db) as conn:
            conn.execute('''
                INSERT INTO sync_history 
                (timestamp, service, operation, success, file_size)
                VALUES (?, ?, ?, ?, ?)
            ''', (time.time(), service, operation, success, data_size))
            
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status and history"""
        status = {
            'services': {
                'google_drive': {
                    'enabled': self.gdrive_sync.sync_enabled,
                    'configured': self.gdrive_sync.sync_folder_id is not None
                },
                'github': {
                    'enabled': self.github_backup.token is not None,
                    'configured': self.github_backup.repo_full_name is not None
                }
            },
            'auto_sync': {
                'enabled': self.auto_sync_enabled,
                'interval': self.sync_interval
            },
            'recent_operations': []
        }
        
        # Get recent sync operations
        with sqlite3.connect(self.sync_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM sync_history 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            
            status['recent_operations'] = [
                {
                    'timestamp': row['timestamp'],
                    'service': row['service'],
                    'operation': row['operation'],
                    'success': bool(row['success']),
                    'file_size': row['file_size']
                }
                for row in cursor.fetchall()
            ]
            
        return status

# Global cloud sync manager
cloud_sync_manager = None

def get_cloud_sync_manager():
    """Get or create cloud sync manager"""
    global cloud_sync_manager
    
    if cloud_sync_manager is None:
        cloud_sync_manager = CloudSyncManager()
        
    return cloud_sync_manager

def setup_cloud_sync(gdrive_credentials: str = None, github_token: str = None):
    """Setup cloud synchronization"""
    manager = get_cloud_sync_manager()
    
    results = {'google_drive': False, 'github': False}
    
    if gdrive_credentials:
        results['google_drive'] = manager.configure_google_drive(gdrive_credentials)
        
    if github_token:
        results['github'] = manager.configure_github_backup(github_token)
        
    return results

def quick_backup():
    """Perform quick backup to all configured services"""
    manager = get_cloud_sync_manager()
    return manager.sync_all_data()

def emergency_restore():
    """Emergency restore from any available backup"""
    manager = get_cloud_sync_manager()
    return manager.restore_from_cloud('auto')

print("Cloud Sync and Backup System loaded!")
