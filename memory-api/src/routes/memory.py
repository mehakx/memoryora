import os
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

memory_bp = Blueprint('memory', __name__)

def get_db_connection():
    """Get SQLite database connection"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'ora_memory.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

@memory_bp.route('/get-context', methods=['POST'])
def get_user_context():
    """Get user context for personalized AI responses"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user profile
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            # New user - create profile
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO users (user_id, first_visit, last_visit, onboarding_complete, total_conversations)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, now, now, False, 0))
            conn.commit()
            
            conn.close()
            return jsonify({
                'is_new_user': True,
                'user_id': user_id,
                'context': 'New user - start onboarding',
                'onboarding_complete': False,
                'suggested_response': "Hi! I'm ORA, your wellness companion. What's your name?"
            })
        
        # Existing user - get recent conversations
        cursor.execute('''
            SELECT user_message, ora_response, emotion, topic, timestamp 
            FROM conversations 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 5
        ''', (user_id,))
        
        recent_conversations = cursor.fetchall()
        
        # Update last visit
        cursor.execute('UPDATE users SET last_visit = ? WHERE user_id = ?', 
                      (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
        
        # Build context string
        context_parts = []
        
        if user['name']:
            context_parts.append(f"User's name: {user['name']}")
        
        if user['personality_type']:
            context_parts.append(f"Personality: {user['personality_type']}")
        
        if user['communication_style']:
            context_parts.append(f"Communication style: {user['communication_style']}")
        
        if user['total_conversations'] > 0:
            context_parts.append(f"Total conversations: {user['total_conversations']}")
        
        # Add recent conversation history
        if recent_conversations:
            context_parts.append("Recent conversation history:")
            for conv in reversed(list(recent_conversations)[-3:]):  # Last 3 conversations
                context_parts.append(f"User: {conv['user_message']}")
                context_parts.append(f"ORA: {conv['ora_response']}")
        
        # Calculate days since last visit
        if user['last_visit']:
            try:
                last_visit = datetime.fromisoformat(user['last_visit'])
                days_since = (datetime.now() - last_visit).days
                if days_since > 0:
                    context_parts.append(f"Days since last conversation: {days_since}")
            except:
                pass
        
        context = "\n".join(context_parts) if context_parts else "Returning user with no previous context"
        
        return jsonify({
            'is_new_user': False,
            'user_id': user_id,
            'name': user['name'],
            'personality_type': user['personality_type'],
            'communication_style': user['communication_style'],
            'onboarding_complete': bool(user['onboarding_complete']),
            'total_conversations': user['total_conversations'],
            'context': context,
            'recent_conversations_count': len(recent_conversations)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/save-conversation', methods=['POST'])
def save_conversation():
    """Save conversation to database"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user_message = data.get('user_message')
        ora_response = data.get('ora_response')
        emotion = data.get('emotion', '')
        topic = data.get('topic', '')
        session_id = data.get('session_id', '')
        
        if not all([user_id, user_message, ora_response]):
            return jsonify({'error': 'user_id, user_message, and ora_response are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Save conversation
        cursor.execute('''
            INSERT INTO conversations (user_id, timestamp, user_message, ora_response, emotion, topic, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, datetime.now().isoformat(), user_message, ora_response, emotion, topic, session_id))
        
        # Update user's total conversation count
        cursor.execute('''
            UPDATE users 
            SET total_conversations = total_conversations + 1, last_visit = ?
            WHERE user_id = ?
        ''', (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'saved',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/update-profile', methods=['POST'])
def update_user_profile():
    """Update user profile information"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        allowed_fields = ['name', 'personality_type', 'communication_style', 'preferences', 'onboarding_complete']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                values.append(data[field])
        
        if update_fields:
            update_fields.append("last_visit = ?")
            values.append(datetime.now().isoformat())
            values.append(user_id)
            
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'status': 'updated',
            'user_id': user_id,
            'updated_fields': list(data.keys())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/get-stats', methods=['POST'])
def get_user_stats():
    """Get user statistics and insights"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user basic info
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get conversation stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_conversations,
                MIN(timestamp) as first_conversation,
                MAX(timestamp) as last_conversation
            FROM conversations 
            WHERE user_id = ?
        ''', (user_id,))
        
        conv_stats = cursor.fetchone()
        
        # Get emotion patterns
        cursor.execute('''
            SELECT emotion, COUNT(*) as count
            FROM conversations 
            WHERE user_id = ? AND emotion != ''
            GROUP BY emotion
            ORDER BY count DESC
            LIMIT 5
        ''', (user_id,))
        
        emotion_patterns = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'user_id': user_id,
            'name': user['name'],
            'member_since': user['first_visit'],
            'last_visit': user['last_visit'],
            'total_conversations': conv_stats['total_conversations'],
            'onboarding_complete': bool(user['onboarding_complete']),
            'personality_type': user['personality_type'],
            'communication_style': user['communication_style'],
            'emotion_patterns': [dict(row) for row in emotion_patterns]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/search-conversations', methods=['POST'])
def search_conversations():
    """Search through user's conversation history"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        query = data.get('query', '')
        limit = data.get('limit', 10)
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if query:
            # Search in messages
            cursor.execute('''
                SELECT user_message, ora_response, emotion, topic, timestamp
                FROM conversations 
                WHERE user_id = ? AND (
                    user_message LIKE ? OR 
                    ora_response LIKE ? OR 
                    topic LIKE ?
                )
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, f'%{query}%', f'%{query}%', f'%{query}%', limit))
        else:
            # Get recent conversations
            cursor.execute('''
                SELECT user_message, ora_response, emotion, topic, timestamp
                FROM conversations 
                WHERE user_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
        
        conversations = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'user_id': user_id,
            'query': query,
            'results': [dict(row) for row in conversations],
            'count': len(conversations)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

