# Manager.py - LSDAI Download Manager
# Handles file downloads with multiple fallback methods

import os
import re
import subprocess
import requests
import shutil
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import time
import json

# Get environment paths
HOME = Path(os.environ.get('home_path', '/content'))
SCR_PATH = Path(os.environ.get('scr_path', HOME / 'LSDAI'))

# Try to import enhanced modules
try:
    from modules.NotificationSystem import send_info, send_success, send_error
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

def send_notification(title, message, type_="info"):
    """Send notification if available"""
    if NOTIFICATIONS_AVAILABLE:
        if type_ == "success":
            send_success(title, message)
        elif type_ == "error":
            send_error(title, message)
        else:
            send_info(title, message)

def get_download_directory(url, webui_type='automatic1111'):
    """Determine the correct download directory based on file type and WebUI"""
    
    # Extract filename from URL
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path).lower()
    
    # Base directories for different WebUI types
    if webui_type == 'ComfyUI':
        base_dirs = {
            'models': HOME / 'ComfyUI' / 'models',
            'checkpoints': HOME / 'ComfyUI' / 'models' / 'checkpoints',
            'vae': HOME / 'ComfyUI' / 'models' / 'vae',
            'lora': HOME / 'ComfyUI' / 'models' / 'loras',
            'embeddings': HOME / 'ComfyUI' / 'models' / 'embeddings',
            'controlnet': HOME / 'ComfyUI' / 'models' / 'controlnet'
        }
    else:  # automatic1111
        base_dirs = {
            'models': HOME / 'stable-diffusion-webui' / 'models' / 'Stable-diffusion',
            'checkpoints': HOME / 'stable-diffusion-webui' / 'models' / 'Stable-diffusion',
            'vae': HOME / 'stable-diffusion-webui' / 'models' / 'VAE',
            'lora': HOME / 'stable-diffusion-webui' / 'models' / 'Lora',
            'embeddings': HOME / 'stable-diffusion-webui' / 'embeddings',
            'controlnet': HOME / 'stable-diffusion-webui' / 'models' / 'ControlNet'
        }
    
    # Determine file type based on filename and URL patterns
    if any(pattern in filename for pattern in ['.safetensors', '.ckpt', '.pt']):
        if 'vae' in filename or 'vae' in url.lower():
            return base_dirs['vae']
        elif any(pattern in filename for pattern in ['lora', 'lyco']):
            return base_dirs['lora']
        elif 'controlnet' in url.lower() or 'control' in filename:
            return base_dirs['controlnet']
        elif any(pattern in filename for pattern in ['embedding', 'textual']):
            return base_dirs['embeddings']
        else:
            return base_dirs['checkpoints']
    elif filename.endswith('.png') or filename.endswith('.jpg'):
        return base_dirs['embeddings']
    else:
        # Default to models directory
        return base_dirs['models']

def clean_filename(filename):
    """Clean filename by removing problematic characters"""
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove excessive whitespace
    filename = re.sub(r'\s+', ' ', filename).strip()
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    return filename

def get_filename_from_url(url):
    """Extract and clean filename from URL"""
    
    try:
        # Parse URL
        parsed_url = urlparse(url)
        
        # Check if it's a CivitAI URL with special handling
        if 'civitai.com' in url:
            return get_civitai_filename(url)
        elif 'huggingface.co' in url:
            return get_huggingface_filename(url)
        
        # Extract filename from path
        filename = os.path.basename(parsed_url.path)
        
        # If no filename in path, try to extract from query parameters
        if not filename or '.' not in filename:
            query_params = parse_qs(parsed_url.query)
            if 'filename' in query_params:
                filename = query_params['filename'][0]
        
        # If still no filename, generate one
        if not filename:
            filename = f"downloaded_file_{int(time.time())}"
        
        return clean_filename(filename)
        
    except Exception as e:
        print(f"Error extracting filename from URL: {e}")
        return f"downloaded_file_{int(time.time())}"

def get_civitai_filename(url):
    """Get filename for CivitAI downloads"""
    try:
        # CivitAI URLs often need special handling
        response = requests.head(url, allow_redirects=True, timeout=10)
        
        # Try to get filename from Content-Disposition header
        if 'Content-Disposition' in response.headers:
            content_disp = response.headers['Content-Disposition']
            filename_match = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disp)
            if filename_match:
                filename = filename_match.group(1).strip('"\'')
                return clean_filename(filename)
        
        # Fallback to URL parsing
        return clean_filename(os.path.basename(urlparse(url).path))
        
    except Exception as e:
        print(f"Error getting CivitAI filename: {e}")
        return f"civitai_model_{int(time.time())}.safetensors"

def get_huggingface_filename(url):
    """Get filename for HuggingFace downloads"""
    try:
        # HuggingFace URLs have predictable structure
        if '/resolve/' in url:
            parts = url.split('/resolve/')[-1].split('/')
            if len(parts) >= 2:
                return clean_filename(parts[-1])
        
        return clean_filename(os.path.basename(urlparse(url).path))
        
    except Exception as e:
        print(f"Error getting HuggingFace filename: {e}")
        return f"huggingface_model_{int(time.time())}"

def download_with_requests(url, filepath, progress_callback=None):
    """Download file using requests with progress tracking"""
    
    try:
        print(f"📥 Downloading with requests: {filepath.name}")
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if progress_callback and total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        progress_callback(progress)
        
        return True
        
    except Exception as e:
        print(f"⚠️ Requests download failed: {e}")
        return False

def download_with_wget(url, filepath):
    """Download file using wget"""
    
    try:
        print(f"📥 Downloading with wget: {filepath.name}")
        
        cmd = ['wget', '-O', str(filepath), url, '--no-check-certificate', '--progress=bar:force']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"⚠️ Wget download failed: {e}")
        return False

def download_with_curl(url, filepath):
    """Download file using curl"""
    
    try:
        print(f"📥 Downloading with curl: {filepath.name}")
        
        cmd = ['curl', '-L', '-o', str(filepath), url, '--progress-bar']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"⚠️ Curl download failed: {e}")
        return False

def download_with_aria2c(url, filepath):
    """Download file using aria2c"""
    
    try:
        print(f"📥 Downloading with aria2c: {filepath.name}")
        
        cmd = [
            'aria2c',
            '--dir', str(filepath.parent),
            '--out', filepath.name,
            '--max-connection-per-server', '4',
            '--split', '4',
            '--continue', 'true',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"⚠️ Aria2c download failed: {e}")
        return False

def verify_download(filepath, min_size=1024):
    """Verify that the downloaded file is valid"""
    
    try:
        if not filepath.exists():
            return False
        
        # Check file size
        file_size = filepath.stat().st_size
        if file_size < min_size:
            print(f"⚠️ Downloaded file too small: {file_size} bytes")
            return False
        
        # Check if file is HTML (error page)
        if filepath.suffix.lower() in ['.safetensors', '.ckpt', '.pt']:
            with open(filepath, 'rb') as f:
                header = f.read(512)
                if b'<html' in header.lower() or b'<body' in header.lower():
                    print(f"⚠️ Downloaded file appears to be HTML (error page)")
                    return False
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error verifying download: {e}")
        return False

def m_download(url, log=False, unzip=False, webui_type='automatic1111', progress_callback=None):
    """
    Main download function with multiple fallback methods
    
    Args:
        url: URL to download
        log: Whether to log the download
        unzip: Whether to unzip after download (not implemented)
        webui_type: Type of WebUI for directory selection
        progress_callback: Function to call with progress updates
    
    Returns:
        bool: True if download successful, False otherwise
    """
    
    if not url or not url.strip():
        print("⚠️ Empty URL provided")
        return False
    
    url = url.strip()
    print(f"🔄 Processing download: {url}")
    
    try:
        # Get filename and directory
        filename = get_filename_from_url(url)
        download_dir = get_download_directory(url, webui_type)
        
        # Ensure download directory exists
        download_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = download_dir / filename
        
        # Check if file already exists
        if filepath.exists() and verify_download(filepath):
            print(f"✅ File already exists: {filepath}")
            if NOTIFICATIONS_AVAILABLE:
                send_notification("Download", f"File already exists: {filename}", "info")
            return True
        
        print(f"📁 Download directory: {download_dir}")
        print(f"📄 Filename: {filename}")
        
        # Try different download methods in order of preference
        download_methods = [
            ('aria2c', lambda: download_with_aria2c(url, filepath)),
            ('requests', lambda: download_with_requests(url, filepath, progress_callback)),
            ('wget', lambda: download_with_wget(url, filepath)),
            ('curl', lambda: download_with_curl(url, filepath))
        ]
        
        for method_name, method_func in download_methods:
            try:
                print(f"🔧 Trying {method_name}...")
                
                if method_func():
                    # Verify download
                    if verify_download(filepath):
                        print(f"✅ Download successful with {method_name}: {filename}")
                        
                        if log:
                            log_download(url, str(filepath), True)
                        
                        if NOTIFICATIONS_AVAILABLE:
                            send_notification("Download Complete", f"Successfully downloaded: {filename}", "success")
                        
                        return True
                    else:
                        print(f"⚠️ Download verification failed for {method_name}")
                        # Clean up invalid file
                        if filepath.exists():
                            filepath.unlink()
                else:
                    print(f"⚠️ {method_name} download failed")
                    
            except Exception as e:
                print(f"⚠️ {method_name} error: {e}")
                continue
        
        # All methods failed
        print(f"❌ All download methods failed for: {url}")
        
        if log:
            log_download(url, str(filepath), False)
        
        if NOTIFICATIONS_AVAILABLE:
            send_notification("Download Failed", f"Could not download: {filename}", "error")
        
        return False
        
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False

def m_clone(input_source, recursive=True, depth=1, log=False):
    """
    Clone a git repository
    
    Args:
        input_source: Git repository URL
        recursive: Whether to clone recursively
        depth: Clone depth (1 for shallow clone)
        log: Whether to log the operation
    
    Returns:
        bool: True if clone successful, False otherwise
    """
    
    if not input_source or not input_source.strip():
        print("⚠️ Empty repository URL provided")
        return False
    
    url = input_source.strip()
    
    try:
        # Extract repository name
        repo_name = os.path.basename(url).replace('.git', '')
        
        # Determine clone directory (extensions for WebUI)
        clone_dir = HOME / 'stable-diffusion-webui' / 'extensions' / repo_name
        
        # Check if already exists
        if clone_dir.exists():
            print(f"✅ Repository already exists: {clone_dir}")
            return True
        
        # Ensure parent directory exists
        clone_dir.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"📥 Cloning repository: {url}")
        print(f"📁 Destination: {clone_dir}")
        
        # Build git clone command
        cmd = ['git', 'clone']
        
        if depth and depth > 0:
            cmd.extend(['--depth', str(depth)])
        
        if recursive:
            cmd.append('--recursive')
        
        cmd.extend([url, str(clone_dir)])
        
        # Execute git clone
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"✅ Repository cloned successfully: {repo_name}")
            
            if log:
                log_clone(url, str(clone_dir), True)
            
            if NOTIFICATIONS_AVAILABLE:
                send_notification("Clone Complete", f"Repository cloned: {repo_name}", "success")
            
            return True
        else:
            print(f"❌ Git clone failed: {result.stderr}")
            
            if log:
                log_clone(url, str(clone_dir), False)
            
            return False
            
    except Exception as e:
        print(f"❌ Clone error: {e}")
        return False

def log_download(url, filepath, success):
    """Log download operation"""
    
    try:
        log_dir = SCR_PATH / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'downloads.json'
        
        log_entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'url': url,
            'filepath': filepath,
            'success': success,
            'type': 'download'
        }
        
        # Read existing log
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Add new entry
        logs.append(log_entry)
        
        # Keep only last 1000 entries
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        # Write back
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
    except Exception as e:
        print(f"Warning: Could not log download: {e}")

def log_clone(url, clone_dir, success):
    """Log clone operation"""
    
    try:
        log_dir = SCR_PATH / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'downloads.json'
        
        log_entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'url': url,
            'filepath': clone_dir,
            'success': success,
            'type': 'clone'
        }
        
        # Read existing log
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Add new entry
        logs.append(log_entry)
        
        # Keep only last 1000 entries
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        # Write back
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
    except Exception as e:
        print(f"Warning: Could not log clone: {e}")

def get_download_stats():
    """Get download statistics"""
    
    try:
        log_file = SCR_PATH / 'logs' / 'downloads.json'
        
        if not log_file.exists():
            return {'total': 0, 'successful': 0, 'failed': 0}
        
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        total = len(logs)
        successful = sum(1 for log in logs if log.get('success', False))
        failed = total - successful
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0
        }
        
    except Exception as e:
        print(f"Error getting download stats: {e}")
        return {'total': 0, 'successful': 0, 'failed': 0}

# Export main functions
__all__ = ['m_download', 'm_clone', 'get_download_stats']
