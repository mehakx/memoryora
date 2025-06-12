import os
import sqlite3
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

memory_bp = Blueprint('memory', __name__)

def get_db_connection():
    """Get SQLite database connection"""
    db_path = os.path.join(os.path.dirname(__file__), 'ora_memory.db')
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
                'total_conversations': 0,
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
        
        context = "\\n".join(context_parts) if context_parts else "Returning user with no previous context"
        
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

@memory_bp.route('/get-all-users', methods=['GET'])
def get_all_users():
    """Get all users for admin panel"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all users with their stats
        cursor.execute('''
            SELECT 
                u.user_id,
                u.name,
                u.personality_type,
                u.communication_style,
                u.first_visit,
                u.last_visit,
                u.total_conversations,
                u.onboarding_complete,
                COUNT(c.id) as actual_conversations
            FROM users u
            LEFT JOIN conversations c ON u.user_id = c.user_id
            GROUP BY u.user_id
            ORDER BY u.last_visit DESC
        ''')
        
        users = cursor.fetchall()
        
        # Get overall stats
        cursor.execute('SELECT COUNT(DISTINCT user_id) as total_users FROM users')
        total_users_result = cursor.fetchone()
        total_users = total_users_result['total_users'] if total_users_result else 0
        
        cursor.execute('SELECT COUNT(*) as total_conversations FROM conversations')
        total_conversations_result = cursor.fetchone()
        total_conversations = total_conversations_result['total_conversations'] if total_conversations_result else 0
        
        # Calculate active today
        today = datetime.now().date().isoformat()
        cursor.execute('SELECT COUNT(DISTINCT user_id) as active_today FROM users WHERE DATE(last_visit) = ?', (today,))
        active_today_result = cursor.fetchone()
        active_today = active_today_result['active_today'] if active_today_result else 0
        
        conn.close()
        
        return jsonify({
            'users': [dict(row) for row in users],
            'stats': {
                'total_users': total_users,
                'total_conversations': total_conversations,
                'active_today': active_today
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/search-conversations', methods=['POST'])
def search_conversations():
    """Search conversations for a specific user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        limit = data.get('limit', 50)
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get conversations for the user
        cursor.execute('''
            SELECT 
                id,
                user_id,
                timestamp,
                user_message,
                ora_response,
                emotion,
                topic,
                session_id
            FROM conversations 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        conversations = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'results': [dict(row) for row in conversations],
            'count': len(conversations),
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/update-profile', methods=['POST'])
def update_profile():
    """Update user profile information"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically based on provided fields
        update_fields = []
        values = []
        
        if 'name' in data:
            update_fields.append('name = ?')
            values.append(data['name'])
        
        if 'personality_type' in data:
            update_fields.append('personality_type = ?')
            values.append(data['personality_type'])
        
        if 'communication_style' in data:
            update_fields.append('communication_style = ?')
            values.append(data['communication_style'])
        
        if 'onboarding_complete' in data:
            update_fields.append('onboarding_complete = ?')
            values.append(data['onboarding_complete'])
        
        if 'preferences' in data:
            update_fields.append('preferences = ?')
            values.append(json.dumps(data['preferences']))
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        # Add last_visit update
        update_fields.append('last_visit = ?')
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
    """Get detailed stats for a specific user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get conversation stats
        cursor.execute('SELECT COUNT(*) as total FROM conversations WHERE user_id = ?', (user_id,))
        total_conversations = cursor.fetchone()['total']
        
        # Get recent activity (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) as recent FROM conversations WHERE user_id = ? AND timestamp > ?', (user_id, week_ago))
        recent_conversations = cursor.fetchone()['recent']
        
        conn.close()
        
        return jsonify({
            'user_id': user_id,
            'name': user['name'],
            'total_conversations': total_conversations,
            'recent_conversations': recent_conversations,
            'first_visit': user['first_visit'],
            'last_visit': user['last_visit'],
            'onboarding_complete': bool(user['onboarding_complete'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500