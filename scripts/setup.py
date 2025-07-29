# ~ setup.py | by ANXETY - PLATFORM AGNOSTIC FIXED VERSION ~

from IPython.display import display, HTML, clear_output
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
from tqdm import tqdm
import nest_asyncio
import importlib
import argparse
import aiohttp
import asyncio
import time
import json
import sys
import os

# --- Civitai API Token ---
# Add your Civitai API token here to permanently store it in the notebook.
# This will override the token set in the widgets.
# Get your token here: https://civitai.com/user/account
CIVITAI_API_TOKEN = "9d333451a6148a1682349e326967efc2"

nest_asyncio.apply()  # Async support for Jupyter


# ======================== CONSTANTS =======================

def detect_platform_home():
    """Detect the appropriate home directory based on platform."""
    if 'COLAB_GPU' in os.environ or '/content' in os.getcwd():
        return Path('/content')
    elif 'KAGGLE_URL_BASE' in os.environ or '/kaggle' in os.getcwd():
        return Path('/kaggle/working')
    elif '/teamspace/' in os.getcwd() or any('LIGHTNING' in k for k in os.environ):
        return Path('/teamspace/studios/this_studio')
    elif '/workspace/' in os.getcwd():
        return Path('/workspace')
    else:
        # Default fallback - try to detect from current working directory
        cwd = Path.cwd()
        if cwd.name == 'LSDAI':
            return cwd.parent
        elif 'content' in cwd.parts:
            return Path('/content')
        else:
            return cwd.parent if cwd.name == 'LSDAI' else cwd

# FIXED: Platform-agnostic path detection and restored project name to LSDAI
HOME = detect_platform_home()
SCR_PATH = HOME / 'LSDAI'
SETTINGS_PATH = SCR_PATH / 'settings.json'
VENV_PATH = HOME / 'venv'
MODULES_FOLDER = SCR_PATH / "modules"

# Add corrected paths to the environment
os.environ.update({
    'home_path': str(HOME),
    'scr_path': str(SCR_PATH),
    'venv_path': str(VENV_PATH),
    'settings_path': str(SETTINGS_PATH)
})

# GitHub configuration
DEFAULT_USER = 'remphanstar'
DEFAULT_REPO = 'LSDAI'
DEFAULT_BRANCH = 'main'
DEFAULT_LANG = 'en'
BASE_GITHUB_URL = "https://raw.githubusercontent.com"

# Environment detection
SUPPORTED_ENVS = {
    'COLAB_GPU': 'Google Colab',
    'KAGGLE_URL_BASE': 'Kaggle',
    'LIGHTNING_AI': 'Lightning.ai'
}

# FIXED: File structure - scripts are now directly in scripts folder
FILE_STRUCTURE = {
    'CSS': ['main-widgets.css', 'download-result.css', 'auto-cleaner.css'],
    'JS': ['main-widgets.js'],
    'modules': [
        'json_utils.py', 'webui_utils.py', 'widget_factory.py',
        'CivitaiAPI.py', 'Manager.py', 'TunnelHub.py', '_season.py',
        'enhanced_model_selector.py'
    ],
    'scripts': [
        'widgets-en.py', 'downloading-en.py', 'webui-installer.py',
        'launch.py', 'download-result.py', 'auto-cleaner.py',
        '_models-data.py', '_xl-models-data.py', 'setup.py',
        'requirements.txt'
    ],
    '__configs__': {
        'A1111': ['config.json', 'ui-config.json', '_extensions.txt'],
        'Classic': ['config.json', 'ui-config.json', '_extensions.txt'],
        'ComfyUI': {
            'Comfy-Manager': ['config.ini'],
            'workflows': ['anxety-workflow.json'],
            '': ['install-deps.py', '_extensions.txt', 'comfy.settings.json']
        },
        'Forge': ['config.json', 'ui-config.json', '_extensions.txt'],
        'ReForge': ['config
