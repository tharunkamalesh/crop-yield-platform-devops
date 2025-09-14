import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import time

class OfflineCache:
    """Offline caching system for storing data locally and syncing when online"""
    
    def __init__(self, db_path: str = 'offline_cache.db'):
        self.db_path = db_path
        self.sync_lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Initialize the offline cache database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables for different data types
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS offline_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    synced BOOLEAN DEFAULT FALSE,
                    sync_attempts INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS offline_weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    synced BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS offline_user_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    data_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    synced BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    priority INTEGER DEFAULT 1,
                    retry_count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing offline cache: {e}")
    
    def store_prediction(self, user_id: int, prediction_data: Dict) -> bool:
        """Store prediction data offline"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO offline_predictions (user_id, data, created_at)
                VALUES (?, ?, ?)
            ''', (user_id, json.dumps(prediction_data), datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing prediction offline: {e}")
            return False
    
    def store_weather_data(self, region: str, weather_data: Dict, expiry_hours: int = 6) -> bool:
        """Store weather data offline with expiry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            expires_at = datetime.now() + timedelta(hours=expiry_hours)
            
            cursor.execute('''
                INSERT INTO offline_weather (region, data, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (region, json.dumps(weather_data), datetime.now(), expires_at))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing weather data offline: {e}")
            return False
    
    def store_user_data(self, user_id: int, data_type: str, data: Dict) -> bool:
        """Store user-related data offline"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO offline_user_data (user_id, data_type, data, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, data_type, json.dumps(data), datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing user data offline: {e}")
            return False
    
    def get_cached_predictions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get cached predictions for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT data, created_at FROM offline_predictions
                WHERE user_id = ? AND synced = FALSE
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            results = []
            for row in cursor.fetchall():
                try:
                    data = json.loads(row[0])
                    data['cached_at'] = row[1]
                    results.append(data)
                except json.JSONDecodeError:
                    continue
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error retrieving cached predictions: {e}")
            return []
    
    def get_cached_weather(self, region: str) -> Optional[Dict]:
        """Get cached weather data for a region if not expired"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT data, created_at, expires_at FROM offline_weather
                WHERE region = ? AND expires_at > ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (region, datetime.now()))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                try:
                    data = json.loads(row[0])
                    data['cached_at'] = row[1]
                    data['expires_at'] = row[2]
                    return data
                except json.JSONDecodeError:
                    return None
            
            return None
            
        except Exception as e:
            print(f"Error retrieving cached weather: {e}")
            return None
    
    def get_cached_user_data(self, user_id: int, data_type: str) -> List[Dict]:
        """Get cached user data of specific type"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT data, created_at FROM offline_user_data
                WHERE user_id = ? AND data_type = ? AND synced = FALSE
                ORDER BY created_at DESC
            ''', (user_id, data_type))
            
            results = []
            for row in cursor.fetchall():
                try:
                    data = json.loads(row[0])
                    data['cached_at'] = row[1]
                    results.append(data)
                except json.JSONDecodeError:
                    continue
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error retrieving cached user data: {e}")
            return []
    
    def add_to_sync_queue(self, operation: str, endpoint: str, data: Dict, priority: int = 1) -> bool:
        """Add operation to sync queue for later processing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sync_queue (operation, endpoint, data, priority, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (operation, endpoint, json.dumps(data), priority, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding to sync queue: {e}")
            return False
    
    def get_sync_queue(self, limit: int = 50) -> List[Dict]:
        """Get pending sync operations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, operation, endpoint, data, priority, retry_count, created_at
                FROM sync_queue
                WHERE retry_count < 3
                ORDER BY priority DESC, created_at ASC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                try:
                    data = json.loads(row[3])
                    results.append({
                        'id': row[0],
                        'operation': row[1],
                        'endpoint': row[2],
                        'data': data,
                        'priority': row[4],
                        'retry_count': row[5],
                        'created_at': row[6]
                    })
                except json.JSONDecodeError:
                    continue
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error retrieving sync queue: {e}")
            return []
    
    def mark_synced(self, table: str, record_id: int) -> bool:
        """Mark a record as successfully synced"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if table == 'predictions':
                cursor.execute('''
                    UPDATE offline_predictions SET synced = TRUE WHERE id = ?
                ''', (record_id,))
            elif table == 'weather':
                cursor.execute('''
                    UPDATE offline_weather SET synced = TRUE WHERE id = ?
                ''', (record_id,))
            elif table == 'user_data':
                cursor.execute('''
                    UPDATE offline_user_data SET synced = TRUE WHERE id = ?
                ''', (record_id,))
            elif table == 'sync_queue':
                cursor.execute('DELETE FROM sync_queue WHERE id = ?', (record_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error marking record as synced: {e}")
            return False
    
    def mark_sync_failed(self, queue_id: int) -> bool:
        """Mark a sync operation as failed and increment retry count"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sync_queue 
                SET retry_count = retry_count + 1
                WHERE id = ?
            ''', (queue_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error marking sync as failed: {e}")
            return False
    
    def cleanup_expired_data(self) -> int:
        """Clean up expired weather data and old synced records"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Remove expired weather data
            cursor.execute('DELETE FROM offline_weather WHERE expires_at < ?', (datetime.now(),))
            expired_weather = cursor.rowcount
            
            # Remove old synced predictions (older than 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            cursor.execute('DELETE FROM offline_predictions WHERE synced = TRUE AND created_at < ?', (thirty_days_ago,))
            old_predictions = cursor.rowcount
            
            # Remove old synced user data (older than 30 days)
            cursor.execute('DELETE FROM offline_user_data WHERE synced = TRUE AND created_at < ?', (thirty_days_ago,))
            old_user_data = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            total_cleaned = expired_weather + old_predictions + old_user_data
            return total_cleaned
            
        except Exception as e:
            print(f"Error cleaning up expired data: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the offline cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Count predictions
            cursor.execute('SELECT COUNT(*) FROM offline_predictions')
            stats['total_predictions'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM offline_predictions WHERE synced = FALSE')
            stats['unsynced_predictions'] = cursor.fetchone()[0]
            
            # Count weather data
            cursor.execute('SELECT COUNT(*) FROM offline_weather')
            stats['total_weather'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM offline_weather WHERE expires_at > ?', (datetime.now(),))
            stats['valid_weather'] = cursor.fetchone()[0]
            
            # Count sync queue
            cursor.execute('SELECT COUNT(*) FROM sync_queue')
            stats['pending_sync'] = cursor.fetchone()[0]
            
            # Count user data
            cursor.execute('SELECT COUNT(*) FROM offline_user_data')
            stats['total_user_data'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM offline_user_data WHERE synced = FALSE')
            stats['unsynced_user_data'] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {}
    
    def clear_all_data(self) -> bool:
        """Clear all cached data (use with caution)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM offline_predictions')
            cursor.execute('DELETE FROM offline_weather')
            cursor.execute('DELETE FROM offline_user_data')
            cursor.execute('DELETE FROM sync_queue')
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error clearing all data: {e}")
            return False

# Global offline cache instance
offline_cache = OfflineCache()
