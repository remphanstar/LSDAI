#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manager.py - Enhanced Download Manager with Robust Error Handling
LSDAI v2.0 Enhancement Suite - Core Download Management Module

FIXED: Complete overhaul with proper timeout management, progress reporting,
and Civitai-specific URL handling to prevent hanging and improve reliability.
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

# Try to import notification system
NOTIFICATIONS_AVAILABLE = False
try:
    from NotificationSystem import send_notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    pass

# Progress callback type
ProgressCallback = Optional[Callable[[int, int], None]]

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
            # Try to get filename from Content-Disposition header
            try:
                response = requests.head(url, allow_redirects=True, timeout=10)
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
            '--no-check-certificate',
            url
        ]
        
        # Execute with reasonable timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min max
        
        if result.returncode == 0:
            print(f"✅ Wget download successful")
            return True
        else:
            print(f"⚠️ Wget failed with return code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
        
    except subprocess.TimeoutExpired:
        print(f"⚠️ Wget download timeout after 30 minutes")
        return False
    except FileNotFoundError:
        print(f"⚠️ Wget not found - install wget to use this download method")
        return False
    except Exception as e:
        print(f"⚠️ Wget download failed: {e}")
        return False

def download_with_curl(url: str, filepath: Path) -> bool:
    """
    Download file using curl with timeout and progress reporting
    
    Args:
        url: Download URL
        filepath: Target file path
        
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        print(f"📥 Downloading with curl: {filepath.name}")
        
        cmd = [
            'curl',
            '--location',
            '--output', str(filepath),
            '--progress-bar',
            '--max-time', '1800',  # 30 minutes
            '--connect-timeout', '30',
            '--retry', '3',
            '--continue-at', '-',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            print(f"✅ Curl download successful")
            return True
        else:
            print(f"⚠️ Curl failed with return code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
        
    except subprocess.TimeoutExpired:
        print(f"⚠️ Curl download timeout after 30 minutes")
        return False
    except FileNotFoundError:
        print(f"⚠️ Curl not found - install curl to use this download method")
        return False
    except Exception as e:
        print(f"⚠️ Curl download failed: {e}")
        return False

def download_with_aria2c(url: str, filepath: Path) -> bool:
    """
    Download file using aria2c with optimized settings
    
    Args:
        url: Download URL
        filepath: Target file path
        
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        print(f"📥 Downloading with aria2c: {filepath.name}")
        
        cmd = [
            'aria2c',
            '--dir', str(filepath.parent),
            '--out', filepath.name,
            '--max-connection-per-server', '4',
            '--split', '4',
            '--continue', 'true',
            '--timeout', '30',
            '--max-overall-download-limit', '0',
            '--file-allocation', 'none',
            url
        ]
        
        # Execute with timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0:
            print(f"✅ Aria2c download successful")
            return True
        else:
            print(f"⚠️ Aria2c failed with return code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
        
    except subprocess.TimeoutExpired:
        print(f"⚠️ Aria2c download timeout after 30 minutes")
        return False
    except FileNotFoundError:
        print(f"⚠️ Aria2c not found - install aria2 to use this download method")
        return False
    except Exception as e:
        print(f"⚠️ Aria2c download failed: {e}")
        return False

def verify_download(filepath: Path, min_size: int = 1024) -> bool:
    """
    Verify that the downloaded file is valid
    
    Args:
        filepath: Path to downloaded file
        min_size: Minimum expected file size in bytes
        
    Returns:
        bool: True if file is valid, False otherwise
    """
    try:
        if not filepath.exists():
            print(f"⚠️ Downloaded file does not exist: {filepath}")
            return False
        
        # Check file size
        file_size = filepath.stat().st_size
        if file_size < min_size:
            print(f"⚠️ Downloaded file too small: {file_size} bytes (minimum: {min_size})")
            return False
        
        # Check for HTML error pages in model files
        if filepath.suffix.lower() in ['.safetensors', '.ckpt', '.pt', '.bin']:
            try:
                with open(filepath, 'rb') as f:
                    header = f.read(1024)
                    if b'<html' in header.lower() or b'<body' in header.lower():
                        print(f"⚠️ Downloaded file appears to be HTML error page")
                        return False
            except:
                pass  # If we can't read the file, assume it's binary and valid
        
        print(f"✅ File verification passed: {format_file_size(file_size)}")
        return True
        
    except Exception as e:
        print(f"⚠️ Error verifying download: {e}")
        return False

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def m_download(url: str, log: bool = False, unzip: bool = False, webui_type: str = 'automatic1111', progress_callback: ProgressCallback = None) -> bool:
    """
    Main download function with multiple fallback methods and enhanced error handling
    
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
        
        # Check if file already exists and is valid
        if filepath.exists() and verify_download(filepath):
            print(f"✅ File already exists and is valid: {filepath}")
            if NOTIFICATIONS_AVAILABLE:
                send_notification("Download", f"File already exists: {filename}", "info")
            return True
        
        print(f"📁 Download directory: {download_dir}")
        print(f"📄 Target filename: {filename}")
        
        # Try different download methods in order of preference
        download_methods = [
            ('requests', lambda: download_with_requests(url, filepath, progress_callback)),
            ('aria2c', lambda: download_with_aria2c(url, filepath)),
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

def m_clone(input_source: str, recursive: bool = True, depth: int = 1, log: bool = False) -> bool:
    """
    Clone a git repository with enhanced error handling
    
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
        
        # Determine clone directory
        clone_dir = HOME / 'stable-diffusion-webui' / 'extensions' / repo_name
        
        # Check if already exists
        if clone_dir.exists():
            print(f"✅ Repository already exists: {clone_dir}")
            return True
        
        print(f"📁 Clone directory: {clone_dir}")
        
        # Ensure parent directory exists
        clone_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Build git clone command
        cmd = ['git', 'clone']
        
        if depth > 0:
            cmd.extend(['--depth', str(depth)])
        
        if not recursive:
            cmd.append('--no-recurse-submodules')
        
        cmd.extend([url, str(clone_dir)])
        
        print(f"🔧 Cloning: {' '.join(cmd)}")
        
        # Execute clone with timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Clone successful: {repo_name}")
            
            if log:
                log_clone(url, str(clone_dir), True)
            
            return True
        else:
            print(f"❌ Clone failed: {result.stderr}")
            
            if log:
                log_clone(url, str(clone_dir), False)
            
            return False
        
    except subprocess.TimeoutExpired:
        print(f"❌ Clone timeout after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Clone error: {e}")
        return False

def log_download(url: str, filepath: str, success: bool):
    """Log download operation to JSON file"""
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

def log_clone(url: str, clone_dir: str, success: bool):
    """Log clone operation to JSON file"""
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

def get_download_stats() -> Dict[str, Any]:
    """Get download statistics from log file"""
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
