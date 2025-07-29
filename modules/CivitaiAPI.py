# CivitaiAPI.py - CivitAI API Integration for LSDAI
# Handles CivitAI model downloads and API interactions

import requests
import json
import time
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional, Union

# Get environment paths
HOME = Path(os.environ.get('home_path', '/content'))
SCR_PATH = Path(os.environ.get('scr_path', HOME / 'LSDAI'))

# Try to import json_utils for token management
try:
    import json_utils as js
    JSON_UTILS_AVAILABLE = True
except ImportError:
    JSON_UTILS_AVAILABLE = False

class CivitAiAPI:
    """CivitAI API client for model downloads and information retrieval"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.base_url = "https://civitai.com/api/v1"
        self.api_token = api_token or self._get_token_from_settings()
        self.session = requests.Session()
        
        # Set up session headers
        if self.api_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_token}',
                'User-Agent': 'LSDAI/2.0'
            })
        else:
            self.session.headers.update({
                'User-Agent': 'LSDAI/2.0'
            })
    
    def _get_token_from_settings(self) -> Optional[str]:
        """Get CivitAI token from settings"""
        if JSON_UTILS_AVAILABLE:
            return js.read_key('civitai_token', '')
        return ''
    
    def set_token(self, token: str):
        """Set CivitAI API token"""
        self.api_token = token
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
        
        # Save to settings if possible
        if JSON_UTILS_AVAILABLE:
            js.write_key('civitai_token', token)
    
    def test_connection(self) -> bool:
        """Test connection to CivitAI API"""
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_model_info(self, model_id: Union[int, str]) -> Optional[Dict]:
        """Get detailed information about a model"""
        try:
            response = self.session.get(f"{self.base_url}/models/{model_id}", timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"Model {model_id} not found")
                return None
            else:
                print(f"Error getting model info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting model info: {e}")
            return None
    
    def get_model_versions(self, model_id: Union[int, str]) -> List[Dict]:
        """Get all versions of a model"""
        try:
            response = self.session.get(f"{self.base_url}/models/{model_id}/versions", timeout=30)
            
            if response.status_code == 200:
                return response.json().get('items', [])
            else:
                print(f"Error getting model versions: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting model versions: {e}")
            return []
    
    def search_models(self, query: str = "", limit: int = 20, page: int = 1, 
                     model_type: str = "", sort: str = "Most Downloaded") -> Dict:
        """Search for models on CivitAI"""
        try:
            params = {
                'limit': limit,
                'page': page
            }
            
            if query:
                params['query'] = query
            if model_type:
                params['types'] = model_type
            if sort:
                params['sort'] = sort
            
            response = self.session.get(f"{self.base_url}/models", params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Search failed: {response.status_code}")
                return {'items': [], 'metadata': {}}
                
        except Exception as e:
            print(f"Search error: {e}")
            return {'items': [], 'metadata': {}}
    
    def get_popular_models(self, model_type: str = "", limit: int = 20) -> List[Dict]:
        """Get popular models from CivitAI"""
        result = self.search_models(
            limit=limit,
            model_type=model_type,
            sort="Most Downloaded"
        )
        return result.get('items', [])
    
    def parse_civitai_url(self, url: str) -> Optional[Dict]:
        """Parse CivitAI URL to extract model and version information"""
        try:
            parsed = urlparse(url)
            
            if 'civitai.com' not in parsed.netloc:
                return None
            
            # Handle different URL formats
            path_parts = parsed.path.strip('/').split('/')
            
            result = {
                'model_id': None,
                'version_id': None,
                'is_direct_download': False
            }
            
            # Direct download URL: /api/download/models/{versionId}
            if 'api/download/models' in parsed.path:
                if len(path_parts) >= 4:
                    result['version_id'] = path_parts[3]
                    result['is_direct_download'] = True
            
            # Model page URL: /models/{modelId}
            elif 'models' in path_parts:
                model_idx = path_parts.index('models')
                if len(path_parts) > model_idx + 1:
                    result['model_id'] = path_parts[model_idx + 1]
            
            # Check for version in query parameters
            query_params = parse_qs(parsed.query)
            if 'modelVersionId' in query_params:
                result['version_id'] = query_params['modelVersionId'][0]
            
            return result
            
        except Exception as e:
            print(f"Error parsing CivitAI URL: {e}")
            return None
    
    def get_download_url(self, version_id: Union[int, str]) -> Optional[str]:
        """Get direct download URL for a model version"""
        try:
            # First get version info to find the download URL
            response = self.session.get(f"{self.base_url}/model-versions/{version_id}", timeout=30)
            
            if response.status_code == 200:
                version_data = response.json()
                files = version_data.get('files', [])
                
                # Find the primary model file
                for file_info in files:
                    if file_info.get('primary', False):
                        download_url = file_info.get('downloadUrl')
                        if download_url:
                            return download_url
                
                # Fallback to first file if no primary file found
                if files:
                    return files[0].get('downloadUrl')
            
            # Fallback: construct direct download URL
            return f"https://civitai.com/api/download/models/{version_id}"
            
        except Exception as e:
            print(f"Error getting download URL: {e}")
            return f"https://civitai.com/api/download/models/{version_id}"
    
    def get_model_filename(self, version_id: Union[int, str]) -> Optional[str]:
        """Get the filename for a model version"""
        try:
            response = self.session.get(f"{self.base_url}/model-versions/{version_id}", timeout=30)
            
            if response.status_code == 200:
                version_data = response.json()
                files = version_data.get('files', [])
                
                # Find the primary model file
                for file_info in files:
                    if file_info.get('primary', False):
                        return file_info.get('name')
                
                # Fallback to first file
                if files:
                    return files[0].get('name')
            
            return None
            
        except Exception as e:
            print(f"Error getting filename: {e}")
            return None
    
    def download_model(self, url: str, destination: Optional[Path] = None) -> bool:
        """Download a model from CivitAI"""
        try:
            url_info = self.parse_civitai_url(url)
            if not url_info:
                print("Invalid CivitAI URL")
                return False
            
            # Get download URL and filename
            if url_info['is_direct_download']:
                download_url = url
                version_id = url_info['version_id']
            else:
                version_id = url_info['version_id']
                if not version_id and url_info['model_id']:
                    # Get latest version of the model
                    versions = self.get_model_versions(url_info['model_id'])
                    if versions:
                        version_id = versions[0]['id']
                
                if not version_id:
                    print("Could not determine version ID")
                    return False
                
                download_url = self.get_download_url(version_id)
            
            if not download_url:
                print("Could not get download URL")
                return False
            
            # Get filename
            filename = self.get_model_filename(version_id)
            if not filename:
                filename = f"civitai_model_{version_id}.safetensors"
            
            # Determine destination
            if destination is None:
                destination = HOME / 'stable-diffusion-webui' / 'models' / 'Stable-diffusion'
            
            destination.mkdir(parents=True, exist_ok=True)
            filepath = destination / filename
            
            # Check if file already exists
            if filepath.exists():
                print(f"File already exists: {filename}")
                return True
            
            print(f"Downloading: {filename}")
            print(f"From: {download_url}")
            
            # Download with progress tracking
            response = self.session.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\rProgress: {progress:.1f}%", end='', flush=True)
            
            print(f"\n✅ Downloaded: {filename}")
            return True
            
        except Exception as e:
            print(f"Download error: {e}")
            return False
    
    def get_user_info(self) -> Optional[Dict]:
        """Get information about the authenticated user"""
        if not self.api_token:
            print("API token required for user info")
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/user", timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("Invalid API token")
                return None
            else:
                print(f"Error getting user info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def get_model_categories(self) -> List[str]:
        """Get available model categories"""
        return [
            "Checkpoint",
            "TextualInversion",
            "Hypernetwork", 
            "AestheticGradient",
            "LORA",
            "Controlnet",
            "Poses"
        ]
    
    def get_trending_models(self, period: str = "Week") -> List[Dict]:
        """Get trending models for a specific time period"""
        valid_periods = ["Day", "Week", "Month", "Year", "AllTime"]
        if period not in valid_periods:
            period = "Week"
        
        result = self.search_models(
            limit=20,
            sort=f"Most Downloaded ({period})"
        )
        return result.get('items', [])
    
    def format_model_info(self, model_data: Dict) -> str:
        """Format model information for display"""
        try:
            name = model_data.get('name', 'Unknown')
            creator = model_data.get('creator', {}).get('username', 'Unknown')
            model_type = model_data.get('type', 'Unknown')
            downloads = model_data.get('stats', {}).get('downloadCount', 0)
            rating = model_data.get('stats', {}).get('rating', 0)
            
            return f"""
📋 Model: {name}
👤 Creator: {creator}
🏷️ Type: {model_type}
📥 Downloads: {downloads:,}
⭐ Rating: {rating:.1f}/5
            """.strip()
            
        except Exception as e:
            return f"Error formatting model info: {e}"
    
    def search_and_display(self, query: str, limit: int = 10):
        """Search for models and display formatted results"""
        print(f"🔍 Searching CivitAI for: {query}")
        print("=" * 50)
        
        results = self.search_models(query, limit=limit)
        models = results.get('items', [])
        
        if not models:
            print("No models found")
            return
        
        for i, model in enumerate(models, 1):
            print(f"\n{i}. {self.format_model_info(model)}")
            print(f"🔗 URL: https://civitai.com/models/{model.get('id')}")
        
        total = results.get('metadata', {}).get('totalItems', len(models))
        print(f"\nShowing {len(models)} of {total} results")

# Convenience functions for easy use
def get_civitai_client(api_token: Optional[str] = None) -> CivitAiAPI:
    """Get a CivitAI API client instance"""
    return CivitAiAPI(api_token)

def download_civitai_model(url: str, destination: Optional[Path] = None, 
                          api_token: Optional[str] = None) -> bool:
    """Download a model from CivitAI URL"""
    client = CivitAiAPI(api_token)
    return client.download_model(url, destination)

def search_civitai_models(query: str, limit: int = 20, api_token: Optional[str] = None) -> List[Dict]:
    """Search for models on CivitAI"""
    client = CivitAiAPI(api_token)
    result = client.search_models(query, limit=limit)
    return result.get('items', [])

def get_civitai_model_info(model_id: Union[int, str], api_token: Optional[str] = None) -> Optional[Dict]:
    """Get information about a CivitAI model"""
    client = CivitAiAPI(api_token)
    return client.get_model_info(model_id)

# Export main classes and functions
__all__ = [
    'CivitAiAPI',
    'get_civitai_client',
    'download_civitai_model', 
    'search_civitai_models',
    'get_civitai_model_info'
]
