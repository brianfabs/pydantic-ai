"""
Database Manager - Handles data persistence
"""

import sqlite3
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class Database:
    """Manages database operations for the application"""
    
    def __init__(self):
        self.db_path = Path("data/agents.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self.connection = None
    
    async def init_db(self):
        """Initialize the database and create tables"""
        try:
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            await self._create_tables()
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
    
    async def _create_tables(self):
        """Create necessary database tables"""
        cursor = self.connection.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                user_message_timestamp TEXT NOT NULL,
                agent_response_timestamp TEXT NOT NULL,
                usage_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Agent stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL UNIQUE,
                total_conversations INTEGER DEFAULT 0,
                total_tokens_used INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # System logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
    
    async def save_conversation(self, agent_id: str, user_message: Dict, agent_message: Dict):
        """Save a conversation to the database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO conversations 
                (agent_id, user_message, agent_response, user_message_timestamp, 
                 agent_response_timestamp, usage_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                agent_id,
                user_message["content"],
                agent_message["content"],
                user_message["timestamp"],
                agent_message["timestamp"],
                json.dumps(agent_message.get("usage")) if agent_message.get("usage") else None
            ))
            
            # Update agent stats
            await self._update_agent_stats(agent_id, agent_message.get("usage"))
            
            self.connection.commit()
            
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    async def _update_agent_stats(self, agent_id: str, usage_data: Optional[Dict]):
        """Update agent statistics"""
        cursor = self.connection.cursor()
        
        # Get current stats
        cursor.execute("SELECT * FROM agent_stats WHERE agent_id = ?", (agent_id,))
        stats = cursor.fetchone()
        
        tokens_used = 0
        if usage_data:
            tokens_used = usage_data.get("total_tokens", 0)
        
        if stats:
            # Update existing stats
            cursor.execute("""
                UPDATE agent_stats 
                SET total_conversations = total_conversations + 1,
                    total_tokens_used = total_tokens_used + ?,
                    last_used = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE agent_id = ?
            """, (tokens_used, agent_id))
        else:
            # Create new stats record
            cursor.execute("""
                INSERT INTO agent_stats 
                (agent_id, total_conversations, total_tokens_used, last_used)
                VALUES (?, 1, ?, CURRENT_TIMESTAMP)
            """, (agent_id, tokens_used))
    
    async def get_conversation_history(self, agent_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for an agent"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE agent_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (agent_id, limit))
            
            rows = cursor.fetchall()
            
            conversations = []
            for row in rows:
                conversations.append({
                    "id": row["id"],
                    "user_message": row["user_message"],
                    "agent_response": row["agent_response"],
                    "user_timestamp": row["user_message_timestamp"],
                    "agent_timestamp": row["agent_response_timestamp"],
                    "usage": json.loads(row["usage_data"]) if row["usage_data"] else None,
                    "created_at": row["created_at"]
                })
            
            return conversations
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    async def get_agent_stats(self, agent_id: str) -> Optional[Dict]:
        """Get statistics for a specific agent"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT * FROM agent_stats WHERE agent_id = ?", (agent_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "agent_id": row["agent_id"],
                    "total_conversations": row["total_conversations"],
                    "total_tokens_used": row["total_tokens_used"],
                    "last_used": row["last_used"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting agent stats: {e}")
            return None
    
    async def get_all_agent_stats(self) -> List[Dict]:
        """Get statistics for all agents"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT * FROM agent_stats ORDER BY last_used DESC")
            rows = cursor.fetchall()
            
            stats = []
            for row in rows:
                stats.append({
                    "agent_id": row["agent_id"],
                    "total_conversations": row["total_conversations"],
                    "total_tokens_used": row["total_tokens_used"],
                    "last_used": row["last_used"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            return stats
            
        except Exception as e:
            print(f"Error getting all agent stats: {e}")
            return []
    
    async def get_total_conversations(self) -> int:
        """Get total number of conversations across all agents"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM conversations")
            row = cursor.fetchone()
            return row["total"] if row else 0
            
        except Exception as e:
            print(f"Error getting total conversations: {e}")
            return 0
    
    async def log_system_event(self, level: str, message: str, details: Optional[Dict] = None):
        """Log a system event"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO system_logs (level, message, details)
                VALUES (?, ?, ?)
            """, (
                level,
                message,
                json.dumps(details) if details else None
            ))
            
            self.connection.commit()
            
        except Exception as e:
            print(f"Error logging system event: {e}")
    
    async def get_system_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent system logs"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT * FROM system_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            
            logs = []
            for row in rows:
                logs.append({
                    "id": row["id"],
                    "level": row["level"],
                    "message": row["message"],
                    "details": json.loads(row["details"]) if row["details"] else None,
                    "timestamp": row["timestamp"]
                })
            
            return logs
            
        except Exception as e:
            print(f"Error getting system logs: {e}")
            return []
    
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old conversation data"""
        try:
            cursor = self.connection.cursor()
            
            # Delete old conversations
            cursor.execute("""
                DELETE FROM conversations 
                WHERE created_at < datetime('now', '-{} days')
            """.format(days))
            
            # Delete old logs
            cursor.execute("""
                DELETE FROM system_logs 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days))
            
            self.connection.commit()
            
            print(f"✅ Cleaned up data older than {days} days")
            
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
