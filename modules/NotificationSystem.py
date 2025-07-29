# Advanced Notification and Alert System
# Save as: modules/NotificationSystem.py

import json_utils as js
from pathlib import Path
import threading
import requests
import sqlite3
import smtplib
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict, deque

class NotificationChannel:
    """Base class for notification channels"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', True)
        
    def send(self, notification: 'Notification') -> bool:
        """Send notification through this channel"""
        raise NotImplementedError
        
    def test_connection(self) -> bool:
        """Test if the channel is properly configured"""
        raise NotImplementedError

class EmailChannel(NotificationChannel):
    """Email notification channel"""
    
    def send(self, notification: 'Notification') -> bool:
        if not self.enabled:
            return False
            
        try:
            smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.config.get('smtp_port', 587)
            username = self.config.get('username')
            password = self.config.get('password')
            to_email = self.config.get('to_email')
            
            if not all([username, password, to_email]):
                return False
                
            # Create message
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = to_email
            msg['Subject'] = f"LSDAI Alert: {notification.title}"
            
            body = f"""
            {notification.message}
            
            Severity: {notification.severity}
            Timestamp: {datetime.fromtimestamp(notification.timestamp).isoformat()}
            Category: {notification.category}
            """
            
            if notification.details:
                body += f"\nDetails: {json.dumps(notification.details, indent=2)}"
                
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False
            
    def test_connection(self) -> bool:
        test_notification = Notification(
            title="Test Notification",
            message="This is a test notification from LSDAI",
            severity="info",
            category="system"
        )
        return self.send(test_notification)

class DiscordWebhookChannel(NotificationChannel):
    """Discord webhook notification channel"""
    
    def send(self, notification: 'Notification') -> bool:
        if not self.enabled:
            return False
            
        try:
            webhook_url = self.config.get('webhook_url')
            if not webhook_url:
                return False
                
            # Discord color mapping
            color_map = {
                'critical': 0xFF0000,  # Red
                'error': 0xFF6600,     # Orange
                'warning': 0xFFFF00,   # Yellow
                'info': 0x0099FF,      # Blue
                'success': 0x00FF00    # Green
            }
            
            embed = {
                "title": f"🤖 LSDAI Alert: {notification.title}",
                "description": notification.message,
                "color": color_map.get(notification.severity, 0x0099FF),
                "timestamp": datetime.fromtimestamp(notification.timestamp).isoformat(),
                "fields": [
                    {
                        "name": "Severity",
                        "value": notification.severity.upper(),
                        "inline": True
                    },
                    {
                        "name": "Category",
                        "value": notification.category,
                        "inline": True
                    }
                ]
            }
            
            if notification.details:
                embed["fields"].append({
                    "name": "Details",
                    "value": f"```json\n{json.dumps(notification.details, indent=2)[:1000]}```",
                    "inline": False
                })
                
            payload = {"embeds": [embed]}
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            print(f"Discord notification failed: {e}")
            return False
            
    def test_connection(self) -> bool:
        test_notification = Notification(
            title="Test Notification",
            message="🧪 This is a test notification from LSDAI",
            severity="info",
            category="system"
        )
        return self.send(test_notification)

class SlackWebhookChannel(NotificationChannel):
    """Slack webhook notification channel"""
    
    def send(self, notification: 'Notification') -> bool:
        if not self.enabled:
            return False
            
        try:
            webhook_url = self.config.get('webhook_url')
            if not webhook_url:
                return False
                
            # Slack emoji mapping
            emoji_map = {
                'critical': '🚨',
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️',
                'success': '✅'
            }
            
            attachment = {
                "color": "#36a64f" if notification.severity == "success" else "#ff0000" if notification.severity in ["critical", "error"] else "#ffaa00",
                "title": f"{emoji_map.get(notification.severity, 'ℹ️')} LSDAI Alert: {notification.title}",
                "text": notification.message,
                "fields": [
                    {
                        "title": "Severity",
                        "value": notification.severity.upper(),
                        "short": True
                    },
                    {
                        "title": "Category", 
                        "value": notification.category,
                        "short": True
                    },
                    {
                        "title": "Timestamp",
                        "value": datetime.fromtimestamp(notification.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                        "short": True
                    }
                ]
            }
            
            if notification.details:
                attachment["fields"].append({
                    "title": "Details",
                    "value": f"```{json.dumps(notification.details, indent=2)[:1000]}```",
                    "short": False
                })
                
            payload = {"attachments": [attachment]}
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Slack notification failed: {e}")
            return False
            
    def test_connection(self) -> bool:
        test_notification = Notification(
            title="Test Notification", 
            message="🧪 This is a test notification from LSDAI",
            severity="info",
            category="system"
        )
        return self.send(test_notification)

class BrowserNotificationChannel(NotificationChannel):
    """Browser notification channel for web interface"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.notifications_queue = deque(maxlen=100)
        
    def send(self, notification: 'Notification') -> bool:
        if not self.enabled:
            return False
            
        try:
            # Add to queue for web interface consumption
            self.notifications_queue.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'severity': notification.severity,
                'category': notification.category,
                'timestamp': notification.timestamp,
                'details': notification.details,
                'read': False
            })
            
            # Trigger browser notification via JavaScript if in notebook
            try:
                from IPython.display import Javascript, display
                
                js_code = f"""
                if (window.enhancedWidgetManager && window.enhancedWidgetManager.showNotification) {{
                    window.enhancedWidgetManager.showNotification(
                        {json.dumps(notification.message)}, 
                        {json.dumps(notification.severity)}
                    );
                }}
                
                // Also try native browser notification API
                if (Notification && Notification.permission === 'granted') {{
                    new Notification({json.dumps(notification.title)}, {{
                        body: {json.dumps(notification.message)},
                        icon: '/static/favicon.ico'
                    }});
                }}
                """
                display(Javascript(js_code))
                
            except Exception:
                pass  # Ignore if not in notebook environment
                
            return True
            
        except Exception as e:
            print(f"Browser notification failed: {e}")
            return False
            
    def get_recent_notifications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent notifications for web interface"""
        return list(self.notifications_queue)[-limit:]
        
    def mark_as_read(self, notification_id: str):
        """Mark notification as read"""
        for notif in self.notifications_queue:
            if notif['id'] == notification_id:
                notif['read'] = True
                break
                
    def test_connection(self) -> bool:
        return True  # Browser notifications don't need testing

class Notification:
    """Notification object"""
    
    def __init__(self, title: str, message: str, severity: str = "info", 
                 category: str = "general", details: Dict[str, Any] = None):
        self.id = f"notif_{int(time.time() * 1000)}"
        self.title = title
        self.message = message
        self.severity = severity  # critical, error, warning, info, success
        self.category = category
        self.timestamp = time.time()
        self.details = details or {}
        self.sent_channels = []

class NotificationRule:
    """Rule for filtering and routing notifications"""
    
    def __init__(self, name: str, conditions: Dict[str, Any], actions: Dict[str, Any]):
        self.name = name
        self.conditions = conditions
        self.actions = actions
        self.enabled = True
        
    def matches(self, notification: Notification) -> bool:
        """Check if notification matches this rule"""
        if not self.enabled:
            return False
            
        # Check severity filter
        if 'severity' in self.conditions:
            allowed_severities = self.conditions['severity']
            if isinstance(allowed_severities, str):
                allowed_severities = [allowed_severities]
            if notification.severity not in allowed_severities:
                return False
                
        # Check category filter
        if 'category' in self.conditions:
            allowed_categories = self.conditions['category']
            if isinstance(allowed_categories, str):
                allowed_categories = [allowed_categories]
            if notification.category not in allowed_categories:
                return False
                
        # Check keyword filter
        if 'keywords' in self.conditions:
            keywords = self.conditions['keywords']
            if isinstance(keywords, str):
                keywords = [keywords]
            
            text_to_search = f"{notification.title} {notification.message}".lower()
            if not any(keyword.lower() in text_to_search for keyword in keywords):
                return False
                
        # Check time-based conditions
        if 'time_range' in self.conditions:
            time_range = self.conditions['time_range']
            current_hour = datetime.now().hour
            
            if 'start_hour' in time_range and 'end_hour' in time_range:
                start = time_range['start_hour']
                end = time_range['end_hour']
                
                if start <= end:
                    if not (start <= current_hour <= end):
                        return False
                else:  # Overnight range
                    if not (current_hour >= start or current_hour <= end):
                        return False
                        
        return True
        
    def get_channels(self) -> List[str]:
        """Get channels to send to when this rule matches"""
        return self.actions.get('channels', [])
        
    def should_suppress(self) -> bool:
        """Check if this rule should suppress the notification"""
        return self.actions.get('suppress', False)

class NotificationManager:
    """Main notification management system"""
    
    def __init__(self):
        self.channels = {}
        self.rules = []
        self.rate_limits = defaultdict(lambda: deque(maxlen=10))
        self.notification_history = deque(maxlen=1000)
        self.db_path = self._init_database()
        self._load_configuration()
        
    def _init_database(self):
        """Initialize notification database"""
        db_path = Path('data/notifications.db')
        db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    details TEXT,
                    sent_channels TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notification_stats (
                    date TEXT PRIMARY KEY,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    count INTEGER DEFAULT 1
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON notifications(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_severity ON notifications(severity)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON notifications(category)')
            
        return db_path
        
    def _load_configuration(self):
        """Load notification configuration"""
        try:
            settings = js.read(js.SETTINGS_PATH)
            notification_config = settings.get('NOTIFICATIONS', {})
            
            # Load channels
            channels_config = notification_config.get('channels', {})
            for channel_name, channel_config in channels_config.items():
                self.add_channel(channel_name, channel_config)
                
            # Load rules
            rules_config = notification_config.get('rules', [])
            for rule_config in rules_config:
                rule = NotificationRule(
                    rule_config['name'],
                    rule_config['conditions'],
                    rule_config['actions']
                )
                self.rules.append(rule)
                
        except Exception as e:
            print(f"Error loading notification configuration: {e}")
            self._setup_default_configuration()
            
    def _setup_default_configuration(self):
        """Setup default notification configuration"""
        # Add browser notification channel by default
        self.add_channel('browser', {
            'type': 'browser',
            'enabled': True
        })
        
        # Add default rules
        self.add_rule('critical_alerts', {
            'severity': ['critical', 'error']
        }, {
            'channels': ['browser']
        })
        
    def add_channel(self, name: str, config: Dict[str, Any]) -> bool:
        """Add notification channel"""
        try:
            channel_type = config.get('type', name)
            
            if channel_type == 'email':
                channel = EmailChannel(name, config)
            elif channel_type == 'discord':
                channel = DiscordWebhookChannel(name, config)
            elif channel_type == 'slack':
                channel = SlackWebhookChannel(name, config)
            elif channel_type == 'browser':
                channel = BrowserNotificationChannel(name, config)
            else:
                print(f"Unknown channel type: {channel_type}")
                return False
                
            self.channels[name] = channel
            return True
            
        except Exception as e:
            print(f"Error adding channel {name}: {e}")
            return False
            
    def add_rule(self, name: str, conditions: Dict[str, Any], actions: Dict[str, Any]) -> bool:
        """Add notification rule"""
        try:
            rule = NotificationRule(name, conditions, actions)
            self.rules.append(rule)
            return True
        except Exception as e:
            print(f"Error adding rule {name}: {e}")
            return False
            
    def send_notification(self, title: str, message: str, severity: str = "info",
                         category: str = "general", details: Dict[str, Any] = None,
                         channels: List[str] = None) -> bool:
        """Send notification"""
        notification = Notification(title, message, severity, category, details)
        
        # Check rate limits
        if self._is_rate_limited(notification):
            return False
            
        # Apply rules to determine channels
        if channels is None:
            channels = self._apply_rules(notification)
            
        # Check if notification should be suppressed
        if self._should_suppress(notification):
            return False
            
        # Send to specified channels
        sent_successfully = False
        for channel_name in channels:
            if channel_name in self.channels:
                try:
                    success = self.channels[channel_name].send(notification)
                    if success:
                        notification.sent_channels.append(channel_name)
                        sent_successfully = True
                except Exception as e:
                    print(f"Error sending to channel {channel_name}: {e}")
                    
        # Store in database and history
        if sent_successfully:
            self._store_notification(notification)
            self.notification_history.append(notification)
            self._update_rate_limit(notification)
            
        return sent_successfully
        
    def _apply_rules(self, notification: Notification) -> List[str]:
        """Apply rules to determine which channels to use"""
        matching_channels = set()
        
        for rule in self.rules:
            if rule.matches(notification):
                matching_channels.update(rule.get_channels())
                
        # If no rules matched, use default channels based on severity
        if not matching_channels:
            if notification.severity in ['critical', 'error']:
                matching_channels.update(['browser'])
            else:
                matching_channels.update(['browser'])
                
        return list(matching_channels)
        
    def _should_suppress(self, notification: Notification) -> bool:
        """Check if notification should be suppressed"""
        for rule in self.rules:
            if rule.matches(notification) and rule.should_suppress():
                return True
        return False
        
    def _is_rate_limited(self, notification: Notification) -> bool:
        """Check if notification is rate limited"""
        key = f"{notification.category}_{notification.severity}"
        recent_notifications = self.rate_limits[key]
        
        # Check if we've sent too many similar notifications recently
        now = time.time()
        recent_count = sum(1 for ts in recent_notifications if now - ts < 300)  # 5 minutes
        
        return recent_count >= 5  # Max 5 notifications per 5 minutes per category/severity
        
    def _update_rate_limit(self, notification: Notification):
        """Update rate limit tracking"""
        key = f"{notification.category}_{notification.severity}"
        self.rate_limits[key].append(time.time())
        
    def _store_notification(self, notification: Notification):
        """Store notification in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO notifications 
                (id, title, message, severity, category, timestamp, details, sent_channels)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                notification.id,
                notification.title,
                notification.message,
                notification.severity,
                notification.category,
                notification.timestamp,
                json.dumps(notification.details),
                json.dumps(notification.sent_channels)
            ))
            
            # Update stats
            date_key = datetime.fromtimestamp(notification.timestamp).strftime('%Y-%m-%d')
            conn.execute('''
                INSERT OR IGNORE INTO notification_stats (date, severity, category, count)
                VALUES (?, ?, ?, 0)
            ''', (date_key, notification.severity, notification.category))
            
            conn.execute('''
                UPDATE notification_stats 
                SET count = count + 1
                WHERE date = ? AND severity = ? AND category = ?
            ''', (date_key, notification.severity, notification.category))
            
    def get_notification_history(self, hours: int = 24, severity: str = None, 
                               category: str = None) -> List[Dict[str, Any]]:
        """Get notification history"""
        since_timestamp = time.time() - (hours * 3600)
        
        query = "SELECT * FROM notifications WHERE timestamp >= ?"
        params = [since_timestamp]
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
            
        if category:
            query += " AND category = ?"
            params.append(category)
            
        query += " ORDER BY timestamp DESC LIMIT 100"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            return [
                {
                    'id': row['id'],
                    'title': row['title'],
                    'message': row['message'],
                    'severity': row['severity'],
                    'category': row['category'],
                    'timestamp': row['timestamp'],
                    'details': json.loads(row['details']) if row['details'] else {},
                    'sent_channels': json.loads(row['sent_channels']) if row['sent_channels'] else []
                }
                for row in cursor.fetchall()
            ]
            
    def get_notification_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get notification statistics"""
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get total counts by severity
            cursor = conn.execute('''
                SELECT severity, SUM(count) as total 
                FROM notification_stats 
                WHERE date >= ?
                GROUP BY severity
            ''', (since_date,))
            
            severity_stats = {row['severity']: row['total'] for row in cursor.fetchall()}
            
            # Get total counts by category
            cursor = conn.execute('''
                SELECT category, SUM(count) as total 
                FROM notification_stats 
                WHERE date >= ?
                GROUP BY category
            ''', (since_date,))
            
            category_stats = {row['category']: row['total'] for row in cursor.fetchall()}
            
            # Get daily trends
            cursor = conn.execute('''
                SELECT date, severity, SUM(count) as total 
                FROM notification_stats 
                WHERE date >= ?
                GROUP BY date, severity
                ORDER BY date
            ''', (since_date,))
            
            daily_trends = defaultdict(dict)
            for row in cursor.fetchall():
                daily_trends[row['date']][row['severity']] = row['total']
                
            return {
                'period_days': days,
                'by_severity': severity_stats,
                'by_category': category_stats,
                'daily_trends': dict(daily_trends),
                'total_notifications': sum(severity_stats.values())
            }
            
    def test_all_channels(self) -> Dict[str, bool]:
        """Test all configured channels"""
        results = {}
        
        for channel_name, channel in self.channels.items():
            try:
                results[channel_name] = channel.test_connection()
            except Exception as e:
                print(f"Error testing channel {channel_name}: {e}")
                results[channel_name] = False
                
        return results

# Global notification manager
notification_manager = None

def get_notification_manager():
    """Get or create notification manager"""
    global notification_manager
    
    if notification_manager is None:
        notification_manager = NotificationManager()
        
    return notification_manager

def send_notification(title: str, message: str, severity: str = "info", 
                     category: str = "general", **kwargs):
    """Quick function to send notification"""
    manager = get_notification_manager()
    return manager.send_notification(title, message, severity, category, **kwargs)

def send_critical_alert(title: str, message: str, **kwargs):
    """Send critical alert"""
    return send_notification(title, message, "critical", **kwargs)

def send_error_alert(title: str, message: str, **kwargs):
    """Send error alert"""
    return send_notification(title, message, "error", **kwargs)

def send_warning(title: str, message: str, **kwargs):
    """Send warning"""
    return send_notification(title, message, "warning", **kwargs)

def send_info(title: str, message: str, **kwargs):
    """Send info notification"""
    return send_notification(title, message, "info", **kwargs)

def send_success(title: str, message: str, **kwargs):
    """Send success notification"""
    return send_notification(title, message, "success", **kwargs)

print("Advanced Notification and Alert System loaded!")
