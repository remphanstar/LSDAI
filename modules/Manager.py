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

def get_filename_from_url(url: str) -> str:
    """
    Extract filename from URL with enhanced Civitai support
    
    Args:
        url: Download URL
        
    Returns:
        str: Extracted or generated filename
    """
    try:
        # Handle Civitai API URLs
        if 'civitai.com/api/download' in url:
            headers = {}
            token = _get_civitai_token()
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            # Try to get filename from Content-Disposition header
            try:
                response = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
                if 'content-disposition' in response.headers:
                    content_disp = response.headers['content-disposition']
                    if 'filename=' in content_disp:
                        filename = content_disp.split('filename=')[1].strip('"')
                        return filename
            except:
                pass
            
            # Fallback: generate filename from model ID
            parsed = urlparse(url)
            if '/models/' in parsed.path:
                model_id = parsed.path.split('/models/')[1]
                return f"civitai_model_{model_id}.safetensors"
        
        # Handle HuggingFace URLs
        elif 'huggingface.co' in url:
            parsed = urlparse(url)
            filename = parsed.path.split('/')[-1]
            if filename and '.' in filename:
                return filename
        
        # Handle standard URLs
        else:
            parsed = urlparse(url)
            filename = parsed.path.split('/')[-1]
            if filename and '.' in filename:
                return filename
        
        # Final fallback: generate timestamp-based filename
        timestamp = int(time.time())
        return f"download_{timestamp}.safetensors"
        
    except Exception as e:
        print(f"⚠️ Error extracting filename from URL: {e}")
        timestamp = int(time.time())
        return f"download_{timestamp}.safetensors"

def get_download_directory(url: str, webui_type: str = 'automatic1111') -> Path:
    """
    Determine appropriate download directory based on URL and WebUI type
    
    Args:
        url: Download URL
        webui_type: WebUI type (automatic1111, ComfyUI, etc.)
        
    Returns:
        Path: Download directory path
    """
    try:
        # WebUI base paths
        webui_paths = {
            'automatic1111': HOME / 'stable-diffusion-webui',
            'ComfyUI': HOME / 'ComfyUI',
            'InvokeAI': HOME / 'InvokeAI'
        }
        
        base_path = webui_paths.get(webui_type, HOME / 'stable-diffusion-webui')
        
        # Determine subdirectory based on URL patterns
        url_lower = url.lower()
        
        if 'controlnet' in url_lower:
            if webui_type == 'automatic1111':
                return base_path / 'models' / 'ControlNet'
            elif webui_type == 'ComfyUI':
                return base_path / 'models' / 'controlnet'
        elif 'vae' in url_lower or 'autoencoder' in url_lower:
            if webui_type == 'automatic1111':
                return base_path / 'models' / 'VAE'
            elif webui_type == 'ComfyUI':
                return base_path / 'models' / 'vae'
        elif 'lora' in url_lower:
            if webui_type == 'automatic1111':
                return base_path / 'models' / 'Lora'
            elif webui_type == 'ComfyUI':
                return base_path / 'models' / 'loras'
        elif 'embedding' in url_lower or 'textual' in url_lower:
            if webui_type == 'automatic1111':
                return base_path / 'embeddings'
            elif webui_type == 'ComfyUI':
                return base_path / 'models' / 'embeddings'
        else:
            # Default to main model directory
            if webui_type == 'automatic1111':
                return base_path / 'models' / 'Stable-diffusion'
            elif webui_type == 'ComfyUI':
                return base_path / 'models' / 'checkpoints'
        
        # Fallback
        return base_path / 'models' / 'Stable-diffusion'
        
    except Exception as e:
        print(f"⚠️ Error determining download directory: {e}")
        return HOME / 'downloads'

def download_with_requests(url: str, filepath: Path, progress_callback: ProgressCallback = None) -> bool:
    """
    Download file using requests with enhanced progress reporting and error handling
    
    Args:
        url: Download URL
        filepath: Target file path
        progress_callback: Optional progress callback function
        
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        print(f"📥 Downloading with requests: {filepath.name}")
        
        # Configure request headers for better compatibility
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Add Civitai token if available for Civitai URLs
        if 'civitai.com' in url:
            token = _get_civitai_token()
            if token:
                headers['Authorization'] = f'Bearer {token}'

        # Create session for better connection handling
        session = requests.Session()
        session.headers.update(headers)
        
        # Start download with streaming
        response = session.get(url, stream=True, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Get total file size
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        print(f"📊 File size: {format_file_size(total_size)}")
        
        # Download with progress tracking
        start_time = time.time()
        last_progress_time = start_time
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # Update progress every second
                    current_time = time.time()
                    if current_time - last_progress_time >= 1.0:
                        if total_size > 0:
                            percentage = (downloaded_size / total_size) * 100
                            speed = downloaded_size / (current_time - start_time)
                            print(f"📈 Progress: {percentage:.1f}% ({format_file_size(downloaded_size)}/{format_file_size(total_size)}) - Speed: {format_file_size(speed)}/s")
                        else:
                            print(f"📈 Downloaded: {format_file_size(downloaded_size)}")
                        
                        last_progress_time = current_time
                        
                        # Call progress callback if provided
                        if progress_callback:
                            progress_callback(downloaded_size, total_size)
        
        # Final progress report
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            avg_speed = downloaded_size / elapsed_time
            print(f"✅ Download completed in {elapsed_time:.1f}s - Average speed: {format_file_size(avg_speed)}/s")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"⚠️ Download timeout after 30 seconds")
        return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Requests download failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Unexpected download error: {e}")
        return False

def download_with_wget(url: str, filepath: Path) -> bool:
    """
    Download file using wget with timeout and progress reporting
    
    Args:
        url: Download URL
        filepath: Target file path
        
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        print(f"📥 Downloading with wget: {filepath.name}")
        
        cmd = [
            'wget',
            '--timeout=30',
            '--tries=3',
            '--continue',
            '--output-document', str(filepath),
            '--progress=bar:force',
            '--no-check-certificate'
        ]

        # Add Civitai token if available
        if 'civitai.com' in url:
            token = _get_civitai_token()
            if token:
                cmd.append(f'--header=Authorization: Bearer {token}')

        cmd.append(url)
        
        # Execute with reasonable timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min max
        
        if result.returncode == 0:
            print(f"✅ Wget download successful")
            return True
        else:
            print
