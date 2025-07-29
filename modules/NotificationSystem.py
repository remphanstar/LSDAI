# NotificationSystem.py - Advanced Notification and Alert System for LSDAI
# Provides cross-platform notifications for various events

import os
import time
import json
from pathlib import Path
from typing import Optional, Dict, List, Callable
from datetime import datetime

# Try to import platform-specific notification libraries
try:
    from IPython.display import display, HTML, Javascript
    IPYTHON_AVAILABLE = True
except ImportError:
    IPYTHON_AVAILABLE = False

# Check if we're in a Colab/Jupyter environment
try:
    from google.colab import output
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

# Get environment paths
HOME = Path(os.environ.get('home_path', '/content'))
SCR_PATH = Path(os.environ.get('scr_path', HOME / 'LSDAI'))
LOGS_PATH = SCR_PATH / 'logs'

class NotificationManager:
    """Manages notifications across different platforms and contexts"""
    
    def __init__(self):
        self.notification_log = LOGS_PATH / 'notifications.json'
        self.callbacks = []
        self.enabled = True
        self.max_log_entries = 1000
        
        # Ensure logs directory exists
        LOGS_PATH.mkdir(parents=True, exist_ok=True)
        
        # Initialize notification log
        if not self.notification_log.exists():
            self._init_log_file()
    
    def _init_log_file(self):
        """Initialize the notification log file"""
        try:
            initial_data = {
                'notifications': [],
                'created': datetime.now().isoformat(),
                'version': '1.0'
            }
            with open(self.notification_log, 'w') as f:
                json.dump(initial_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not initialize notification log: {e}")
    
    def add_callback(self, callback: Callable):
        """Add a callback function to be called on notifications"""
        self.callbacks.append(callback)
    
    def enable(self):
        """Enable notifications"""
        self.enabled = True
    
    def disable(self):
        """Disable notifications"""
        self.enabled = False
    
    def _log_notification(self, title: str, message: str, notification_type: str):
        """Log notification to file"""
        try:
            # Read existing log
            if self.notification_log.exists():
                with open(self.notification_log, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'notifications': []}
            
            # Add new notification
            notification_entry = {
                'timestamp': datetime.now().isoformat(),
                'title': title,
                'message': message,
                'type': notification_type
            }
            
            log_data['notifications'].append(notification_entry)
            
            # Keep only recent entries
            if len(log_data['notifications']) > self.max_log_entries:
                log_data['notifications'] = log_data['notifications'][-self.max_log_entries:]
            
            # Write back to file
            with open(self.notification_log, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not log notification: {e}")
    
    def _call_callbacks(self, title: str, message: str, notification_type: str):
        """Call all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(title, message, notification_type)
            except Exception as e:
                print(f"Warning: Notification callback failed: {e}")
    
    def _display_console(self, title: str, message: str, notification_type: str):
        """Display notification in console"""
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        icon = icons.get(notification_type, 'ℹ️')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f"[{timestamp}] {icon} {title}: {message}")
    
    def _display_html(self, title: str, message: str, notification_type: str):
        """Display notification as HTML in Jupyter/Colab"""
        if not IPYTHON_AVAILABLE:
            return
        
        colors = {
            'info': '#d1ecf1',
            'success': '#d4edda',
            'warning': '#fff3cd',
            'error': '#f8d7da'
        }
        
        text_colors = {
            'info': '#0c5460',
            'success': '#155724',
            'warning': '#856404',
            'error': '#721c24'
        }
        
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        bg_color = colors.get(notification_type, '#d1ecf1')
        text_color = text_colors.get(notification_type, '#0c5460')
        icon = icons.get(notification_type, 'ℹ️')
        
        notification_html = f"""
        <div style="
            background-color: {bg_color};
            border: 1px solid #bee5eb;
            border-radius: 0.5rem;
            padding: 1rem 1.25rem;
            margin: 0.5rem 0;
            color: {text_color};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            animation: slideIn 0.3s ease-out;
        ">
            <div style="display: flex; align-items: center;">
                <span style="margin-right: 0.75rem; font-size: 1.2em;">{icon}</span>
                <div>
                    <strong style="font-size: 1.1em; margin-bottom: 0.25rem; display: block;">{title}</strong>
                    <div style="font-size: 0.95em; opacity: 0.9;">{message}</div>
                </div>
            </div>
        </div>
        <style>
            @keyframes slideIn {{
                from {{ transform: translateY(-10px); opacity: 0; }}
                to {{ transform: translateY(0); opacity: 1; }}
            }}
        </style>
        """
        
        display(HTML(notification_html))
    
    def _display_javascript_popup(self, title: str, message: str, notification_type: str):
        """Display notification using JavaScript in browser"""
        if not IPYTHON_AVAILABLE or not IN_COLAB:
            return
        
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        icon = icons.get(notification_type, 'ℹ️')
        
        js_code = f"""
        // Create notification popup
        function showNotification() {{
            const notification = document.createElement('div');
            notification.innerHTML = `
                <div style="
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border: 2px solid #007bff;
                    border-radius: 8px;
                    padding: 15px 20px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    z-index: 10000;
                    max-width: 300px;
                    font-family: system-ui, -apple-system, sans-serif;
                    animation: slideInRight 0.3s ease-out;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="margin-right: 8px; font-size: 1.2em;">{icon}</span>
                        <strong style="color: #333;">{title}</strong>
                    </div>
                    <div style="color: #666; font-size: 0.9em;">{message}</div>
                </div>
            `;
            
            document.body.appendChild(notification);
            
            // Auto-remove after 4 seconds
            setTimeout(() => {{
                if (notification.parentNode) {{
                    notification.style.animation = 'slideOutRight 0.3s ease-in';
                    setTimeout(() => {{
                        if (notification.parentNode) {{
                            notification.parentNode.removeChild(notification);
                        }}
                    }}, 300);
                }}
            }}, 4000);
        }}
        
        // Add CSS animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {{
                from {{ transform: translateX(100%); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
            @keyframes slideOutRight {{
                from {{ transform: translateX(0); opacity: 1; }}
                to {{ transform: translateX(100%); opacity: 0; }}
            }}
        `;
        document.head.appendChild(style);
        
        showNotification();
        """
        
        display(Javascript(js_code))
    
    def notify(self, title: str, message: str, notification_type: str = 'info', 
              display_method: str = 'auto'):
        """
        Send a notification
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification ('info', 'success', 'warning', 'error')
            display_method: How to display ('auto', 'console', 'html', 'popup', 'all')
        """
        if not self.enabled:
            return
        
        # Log the notification
        self._log_notification(title, message, notification_type)
        
        # Call callbacks
        self._call_callbacks(title, message, notification_type)
        
        # Display based on method
        if display_method == 'auto':
            # Auto-select best display method
            if IPYTHON_AVAILABLE:
                self._display_html(title, message, notification_type)
            else:
                self._display_console(title, message, notification_type)
        elif display_method == 'console':
            self._display_console(title, message, notification_type)
        elif display_method == 'html':
            self._display_html(title, message, notification_type)
        elif display_method == 'popup':
            self._display_javascript_popup(title, message, notification_type)
        elif display_method == 'all':
            self._display_console(title, message, notification_type)
            self._display_html(title, message, notification_type)
    
    def get_recent_notifications(self, count: int = 10) -> List[Dict]:
        """Get recent notifications from log"""
        try:
            if not self.notification_log.exists():
                return []
            
            with open(self.notification_log, 'r') as f:
                log_data = json.load(f)
            
            notifications = log_data.get('notifications', [])
            return notifications[-count:]
            
        except Exception as e:
            print(f"Error reading notification log: {e}")
            return []
    
    def clear_log(self):
        """Clear notification log"""
        try:
            self._init_log_file()
            print("✅ Notification log cleared")
        except Exception as e:
            print(f"Error clearing notification log: {e}")

# Global notification manager instance
_notification_manager = NotificationManager()

# Convenience functions for easy use
def send_info(title: str, message: str, display_method: str = 'auto'):
    """Send an info notification"""
    _notification_manager.notify(title, message, 'info', display_method)

def send_success(title: str, message: str, display_method: str = 'auto'):
    """Send a success notification"""
    _notification_manager.notify(title, message, 'success', display_method)

def send_warning(title: str, message: str, display_method: str = 'auto'):
    """Send a warning notification"""
    _notification_manager.notify(title, message, 'warning', display_method)

def send_error(title: str, message: str, display_method: str = 'auto'):
    """Send an error notification"""
    _notification_manager.notify(title, message, 'error', display_method)

def enable_notifications():
    """Enable notifications globally"""
    _notification_manager.enable()

def disable_notifications():
    """Disable notifications globally"""
    _notification_manager.disable()

def add_notification_callback(callback: Callable):
    """Add a callback for notifications"""
    _notification_manager.add_callback(callback)

def get_recent_notifications(count: int = 10) -> List[Dict]:
    """Get recent notifications"""
    return _notification_manager.get_recent_notifications(count)

def clear_notification_log():
    """Clear the notification log"""
    _notification_manager.clear_log()

# Enhanced notification functions with more context
def notify_download_start(filename: str):
    """Notify that a download has started"""
    send_info("Download Started", f"Downloading: {filename}")

def notify_download_complete(filename: str, size: str = ""):
    """Notify that a download has completed"""
    size_info = f" ({size})" if size else ""
    send_success("Download Complete", f"Successfully downloaded: {filename}{size_info}")

def notify_download_failed(filename: str, error: str = ""):
    """Notify that a download has failed"""
    error_info = f" - {error}" if error else ""
    send_error("Download Failed", f"Failed to download: {filename}{error_info}")

def notify_install_complete(component: str):
    """Notify that an installation has completed"""
    send_success("Installation Complete", f"{component} installed successfully")

def notify_install_failed(component: str, error: str = ""):
    """Notify that an installation has failed"""
    error_info = f" - {error}" if error else ""
    send_error("Installation Failed", f"Failed to install {component}{error_info}")

def notify_webui_launched(webui_type: str, url: str = ""):
    """Notify that WebUI has been launched"""
    url_info = f" at {url}" if url else ""
    send_success("WebUI Launched", f"{webui_type} WebUI started{url_info}")

def notify_webui_failed(webui_type: str, error: str = ""):
    """Notify that WebUI launch failed"""
    error_info = f" - {error}" if error else ""
    send_error("WebUI Launch Failed", f"Failed to start {webui_type}{error_info}")

def notify_system_info(message: str):
    """Send system information notification"""
    send_info("System Info", message)

def notify_user_action(action: str, details: str = ""):
    """Notify about user actions"""
    details_info = f" - {details}" if details else ""
    send_info("User Action", f"{action}{details_info}")

# Progress notification class
class ProgressNotifier:
    """Handle progress notifications for long-running operations"""
    
    def __init__(self, title: str, total_steps: int = 100):
        self.title = title
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        
        send_info(self.title, "Starting...")
    
    def update(self, step: int = None, message: str = ""):
        """Update progress"""
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
        
        progress_percent = (self.current_step / self.total_steps) * 100
        elapsed_time = time.time() - self.start_time
        
        if self.current_step > 0:
            eta_seconds = (elapsed_time / self.current_step) * (self.total_steps - self.current_step)
            eta_str = f" - ETA: {eta_seconds:.0f}s"
        else:
            eta_str = ""
        
        progress_msg = f"Progress: {progress_percent:.1f}% ({self.current_step}/{self.total_steps}){eta_str}"
        if message:
            progress_msg += f" - {message}"
        
        send_info(self.title, progress_msg, 'console')  # Use console to avoid spam
    
    def complete(self, message: str = "Completed successfully"):
        """Mark as complete"""
        elapsed_time = time.time() - self.start_time
        final_message = f"{message} (took {elapsed_time:.1f}s)"
        send_success(self.title, final_message)
    
    def fail(self, error: str = "Operation failed"):
        """Mark as failed"""
        elapsed_time = time.time() - self.start_time
        final_message = f"{error} (after {elapsed_time:.1f}s)"
        send_error(self.title, final_message)

# Export main functions and classes
__all__ = [
    'NotificationManager', 'ProgressNotifier',
    'send_info', 'send_success', 'send_warning', 'send_error',
    'enable_notifications', 'disable_notifications',
    'add_notification_callback', 'get_recent_notifications', 'clear_notification_log',
    'notify_download_start', 'notify_download_complete', 'notify_download_failed',
    'notify_install_complete', 'notify_install_failed',
    'notify_webui_launched', 'notify_webui_failed',
    'notify_system_info', 'notify_user_action'
]
