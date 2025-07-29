#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manager.py - Enhanced Download Manager with Robust Error Handling
LSDAI v2.0 Enhancement Suite - Core Download Management Module

FIXED: Complete overhaul with proper timeout management, progress reporting,
and Civitai-specific URL handling to prevent hanging and improve reliability.
ADDED: Civitai API token integration for authorized downloads.
"""

import os
import sys
import json
import time
import requests
import subprocess
import shlex
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import Optional, Callable, Dict, Any
import threading

# Get environment paths
HOME = Path(os.environ.get('home_path', '/content'))
SCR_PATH = Path(os.environ.get('scr_path', HOME / 'LSDAI'))
VENV_PATH = Path(os.environ.get('venv_path', HOME / 'venv'))
SETTINGS_PATH = Path(os.environ.get('settings_path', SCR_PATH / 'settings.json'))


# Try to import notification system
NOTIFICATIONS_AVAILABLE = False
try:
    from NotificationSystem import send_notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    pass

# Try to import json_utils for token management
try:
    import json_utils as js
    JSON_UTILS_AVAILABLE = True
except ImportError:
    JSON_UTILS_AVAILABLE = False


# Progress callback type
ProgressCallback = Optional[Callable[[int, int], None]]

def _get_civitai_token() -> Optional[str]:
    """Safely get the Civitai API token from settings."""
    if JSON_UTILS_AVAILABLE and SETTINGS_PATH.exists():
        token = js.read(SETTINGS_PATH, 'WIDGETS.civitai_token', None)
        # Ensure token is not a placeholder and is a non-empty string
        if isinstance(token, str) and token.strip():
            return token.strip()
    return None

def format_file_size(size_bytes: int) -> str:
    """Formats file size in bytes to a human-readable string."""
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(abs(size_bytes).bit_length() / 10)
    power = 1024 ** i
    size = round(size_bytes / power, 2)
    return f"{size} {size_name[i]}"

def get_filename_from_url(url: str) -> str:
    """Extract filename from URL with enhanced Civitai support"""
    try:
        # Handle Civitai API URLs
        if 'civitai.com/api/download' in url:
            headers = {}
            token = _get_civitai_token()
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            try:
                with requests.head(url, headers=headers, allow_redirects=True, timeout=10) as response:
                    if 'content-disposition' in response.headers:
                        content_disp = response.headers['content-disposition']
                        if 'filename=' in content_disp:
                            filename = content_disp.split('filename=')[1].strip('"')
                            return filename
            except requests.exceptions.RequestException:
                pass
            
            parsed = urlparse(url)
            if '/models/' in parsed.path:
                model_id = parsed.path.split('/models/')[1]
                return f"civitai_model_{model_id}.safetensors"
        
        # Handle other URLs
        parsed = urlparse(url)
        filename = parsed.path.split('/')[-1]
        if filename and '.' in filename:
            return filename
        
        timestamp = int(time.time())
        return f"download_{timestamp}.tmp"
        
    except Exception as e:
        print(f"⚠️ Error extracting filename from URL: {e}")
        timestamp = int(time.time())
        return f"download_{timestamp}.tmp"

def get_download_directory(url: str, webui_type: str = 'automatic1111') -> Path:
    """Determine appropriate download directory based on URL and WebUI type"""
    try:
        webui_paths = {
            'automatic1111': HOME / 'stable-diffusion-webui',
            'ComfyUI': HOME / 'ComfyUI',
            'InvokeAI': HOME / 'InvokeAI'
        }
        base_path = webui_paths.get(webui_type, HOME / 'stable-diffusion-webui')
        
        url_lower = url.lower()
        if 'controlnet' in url_lower:
            return base_path / ('models/ControlNet' if webui_type == 'automatic1111' else 'models/controlnet')
        elif 'vae' in url_lower:
            return base_path / ('models/VAE' if webui_type == 'automatic1111' else 'models/vae')
        elif 'lora' in url_lower:
            return base_path / ('models/Lora' if webui_type == 'automatic1111' else 'models/loras')
        elif 'embedding' in url_lower:
            return base_path / ('embeddings' if webui_type == 'automatic1111' else 'models/embeddings')
        else:
            return base_path / ('models/Stable-diffusion' if webui_type == 'automatic1111' else 'models/checkpoints')
    except Exception as e:
        print(f"⚠️ Error determining download directory: {e}")
        return HOME / 'downloads'

def verify_download(filepath: Path, min_size_bytes: int = 1024) -> bool:
    """Verify downloaded file integrity."""
    if not filepath.exists():
        return False
    if filepath.stat().st_size < min_size_bytes:
        print(f"⚠️ Downloaded file too small: {filepath.stat().st_size} bytes (minimum: {min_size_bytes})")
        return False
    # A more robust check could involve checksums if available
    return True

def download_with_requests(url: str, filepath: Path, progress_callback: ProgressCallback = None) -> bool:
    """Download file using requests with progress reporting and error handling."""
    try:
        print(f"📥 Downloading with requests: {filepath.name}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        if 'civitai.com' in url and (token := _get_civitai_token()):
            headers['Authorization'] = f'Bearer {token}'

        with requests.get(url, stream=True, timeout=30, headers=headers, allow_redirects=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            print(f"📊 File size: {format_file_size(total_size)}")
            downloaded_size = 0
            start_time = time.time()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded_size, total_size)
            
            elapsed_time = time.time() - start_time
            avg_speed = downloaded_size / elapsed_time if elapsed_time > 0 else 0
            print(f"✅ Download completed in {elapsed_time:.1f}s - Avg speed: {format_file_size(avg_speed)}/s")
            return verify_download(filepath)

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Requests download failed: {e}")
        return False

def download_with_wget(url: str, filepath: Path) -> bool:
    """Download file using wget."""
    try:
        print(f"📥 Downloading with wget: {filepath.name}")
        cmd = ['wget', '--timeout=30', '--tries=3', '-O', str(filepath), url]
        if 'civitai.com' in url and (token := _get_civitai_token()):
            cmd.insert(1, f'--header=Authorization: Bearer {token}')
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode == 0:
            print("✅ Wget download successful")
            return verify_download(filepath)
        else:
            print(f"⚠️ Wget failed with return code {result.returncode}")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("⚠️ Wget not found - install wget to use this download method")
        return False
    except Exception as e:
        print(f"⚠️ wget download failed: {e}")
        return False

def download_with_aria2c(url: str, filepath: Path) -> bool:
    """Download file using aria2c."""
    try:
        print(f"📥 Downloading with aria2c: {filepath.name}")
        cmd = ['aria2c', '-x', '16', '-s', '16', '-k', '1M', '--out', str(filepath), url]
        if 'civitai.com' in url and (token := _get_civitai_token()):
            cmd.insert(1, f'--header=Authorization: Bearer {token}')
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode == 0:
            print("✅ aria2c download successful")
            return verify_download(filepath)
        else:
            print(f"⚠️ aria2c failed with return code {result.returncode}")
            return False
    except FileNotFoundError:
        print("⚠️ aria2c not found - install aria2 to use this download method")
        return False
    except Exception as e:
        print(f"⚠️ aria2c download failed: {e}")
        return False

def download_with_curl(url: str, filepath: Path) -> bool:
    """Download file using curl."""
    try:
        print(f"📥 Downloading with curl: {filepath.name}")
        cmd = ['curl', '-L', '-o', str(filepath), url]
        if 'civitai.com' in url and (token := _get_civitai_token()):
            cmd.insert(1, '-H')
            cmd.insert(2, f'Authorization: Bearer {token}')

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode == 0:
            print("✅ Curl download successful")
            return verify_download(filepath)
        else:
            print(f"⚠️ Curl failed with return code {result.returncode}")
            return False
    except FileNotFoundError:
        print("⚠️ curl not found - install curl to use this download method")
        return False
    except Exception as e:
        print(f"⚠️ curl download failed: {e}")
        return False

def m_download(url: str, log: bool = False, unzip: bool = False) -> bool:
    """Master download function trying multiple methods."""
    webui_type = js.read(SETTINGS_PATH, 'WEBUI.current', 'automatic1111')
    download_dir = get_download_directory(url, webui_type)
    download_dir.mkdir(parents=True, exist_ok=True)
    filename = get_filename_from_url(url)
    filepath = download_dir / filename
    
    if filepath.exists() and verify_download(filepath):
        print(f"✅ File already exists and is valid: {filename}")
        return True

    download_methods = [
        ("requests", download_with_requests),
        ("aria2c", download_with_aria2c),
        ("wget", download_with_wget),
        ("curl", download_with_curl),
    ]

    for name, method in download_methods:
        print(f"🔧 Trying {name}...")
        if method(url, filepath):
            if unzip and filepath.suffix == '.zip':
                print(f"📦 Unzipping {filepath.name}...")
                shutil.unpack_archive(str(filepath), str(download_dir))
                filepath.unlink() # remove zip after extraction
            return True
        else:
            print(f"⚠️ {name} download failed")
            if filepath.exists(): # Clean up failed partial downloads
                filepath.unlink()

    print(f"❌ All download methods failed for: {url}")
    if NOTIFICATIONS_AVAILABLE:
        send_notification("Download Failed", f"Failed to download {filename}", "error")
    return False

def m_clone(repo_url: str, dest_path: Optional[Path] = None, depth: int = 1) -> bool:
    """Clones a git repository."""
    if dest_path is None:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        dest_path = HOME / repo_name
    
    if dest_path.exists():
        print(f"✅ Directory already exists: {dest_path.name}")
        return True

    try:
        print(f"Cloning {repo_url}...")
        subprocess.run(['git', 'clone', f'--depth={depth}', repo_url, str(dest_path)], check=True)
        print("✅ Clone successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Clone failed: {e}")
        return False
