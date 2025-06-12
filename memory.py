import os
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

memory_bp = Blueprint('memory', __name__)

def get_data_file_path():
    """Get path to JSON data file"""
    return os.path.join(os.path.dirname(__file__), 'ora_memory.json')

def load_data():
    """Load data from JSON file"""
    data_file = get_data_file_path()
    if not os.path.exists(data_file):
        return {'users': {}, 'conversations': []}
    
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except:
        return {'users': {}, 'conversations': []}

def save_data(data):
    """Save data to JSON file"""
    data_file = get_data_file_path()
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)

@memory_bp.route('/get-context', methods=['POST'])
def get_user_context():
    """Get user context for personalized AI responses"""
    try:
        request_data = request.get_json()
        user_id = request_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        data = load_data()
        
        if user_id not in data['users']:
            # New user - create profile
            now = datetime.now().isoformat()
            data['users'][user_id] = {
                'user_id': user_id,
                'name': None,
                'personality_type': None,
                'communication_style': None,
                'first_visit': now,
                'last_visit': now,
                'onboarding_complete': False,
                'total_conversations': 0,
                'preferences': None
            }
            save_data(data)
            
            return jsonify({
                'is_new_user': True,
                'user_id': user_id,
                'context': 'New user - start onboarding',
                'onboarding_complete': False,
                'total_conversations': 0,
                'suggested_response': "Hi! I'm ORA, your wellness companion. What's your name?"
            })
        
        user = data['users'][user_id]
        
        # Get recent conversations
        user_conversations = [conv for conv in data['conversations'] if conv['user_id'] == user_id]
        recent_conversations = sorted(user_conversations, key=lambda x: x['timestamp'], reverse=True)[:5]
        
        # Update last visit
        user['last_visit'] = datetime.now().isoformat()
        save_data(data)
        
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
            for conv in reversed(recent_conversations[-3:]):  # Last 3 conversations
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
    """Save conversation to JSON file"""
    try:
        request_data = request.get_json()
        user_id = request_data.get('user_id')
        user_message = request_data.get('user_message')
        ora_response = request_data.get('ora_response')
        emotion = request_data.get('emotion', '')
        topic = request_data.get('topic', '')
        session_id = request_data.get('session_id', '')
        
        if not all([user_id, user_message, ora_response]):
            return jsonify({'error': 'user_id, user_message, and ora_response are required'}), 400
        
        data = load_data()
        
        # Create conversation record
        conversation = {
            'id': len(data['conversations']) + 1,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'ora_response': ora_response,
            'emotion': emotion,
            'topic': topic,
            'session_id': session_id
        }
        
        data['conversations'].append(conversation)
        
        # Update user's total conversation count
        if user_id in data['users']:
            data['users'][user_id]['total_conversations'] += 1
            data['users'][user_id]['last_visit'] = datetime.now().isoformat()
        
        save_data(data)
        
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
        data = load_data()
        
        users = []
        for user_id, user_data in data['users'].items():
            # Count actual conversations
            actual_conversations = len([conv for conv in data['conversations'] if conv['user_id'] == user_id])
            user_info = user_data.copy()
            user_info['actual_conversations'] = actual_conversations
            users.append(user_info)
        
        # Sort by last visit
        users.sort(key=lambda x: x.get('last_visit', ''), reverse=True)
        
        # Get overall stats
        total_users = len(data['users'])
        total_conversations = len(data['conversations'])
        
        # Calculate active today
        today = datetime.now().date().isoformat()
        active_today = sum(1 for user in data['users'].values() 
                          if user.get('last_visit', '').startswith(today))
        
        return jsonify({
            'users': users,
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
        request_data = request.get_json()
        user_id = request_data.get('user_id')
        limit = request_data.get('limit', 50)
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        data = load_data()
        
        # Get conversations for the user
        user_conversations = [conv for conv in data['conversations'] if conv['user_id'] == user_id]
        user_conversations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit
        conversations = user_conversations[:limit]
        
        return jsonify({
            'results': conversations,
            'count': len(conversations),
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/update-profile', methods=['POST'])
def update_profile():
    """Update user profile information"""
    try:
        request_data = request.get_json()
        user_id = request_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        data = load_data()
        
        # Ensure user exists
        if user_id not in data['users']:
            now = datetime.now().isoformat()
            data['users'][user_id] = {
                'user_id': user_id,
                'name': None,
                'personality_type': None,
                'communication_style': None,
                'first_visit': now,
                'last_visit': now,
                'onboarding_complete': False,
                'total_conversations': 0,
                'preferences': None
            }
        
        user = data['users'][user_id]
        
        # Update fields
        if 'name' in request_data:
            user['name'] = request_data['name']
        
        if 'personality_type' in request_data:
            user['personality_type'] = request_data['personality_type']
        
        if 'communication_style' in request_data:
            user['communication_style'] = request_data['communication_style']
        
        if 'onboarding_complete' in request_data:
            user['onboarding_complete'] = request_data['onboarding_complete']
        
        if 'preferences' in request_data:
            user['preferences'] = request_data['preferences']
        
        # Update last visit
        user['last_visit'] = datetime.now().isoformat()
        
        save_data(data)
        
        return jsonify({
            'status': 'updated',
            'user_id': user_id,
            'updated_fields': list(request_data.keys())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@memory_bp.route('/get-stats', methods=['POST'])
def get_user_stats():
    """Get detailed stats for a specific user"""
    try:
        request_data = request.get_json()
        user_id = request_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        data = load_data()
        
        if user_id not in data['users']:
            return jsonify({'error': 'User not found'}), 404
        
        user = data['users'][user_id]
        
        # Get conversation stats
        user_conversations = [conv for conv in data['conversations'] if conv['user_id'] == user_id]
        total_conversations = len(user_conversations)
        
        # Get recent activity (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_conversations = len([conv for conv in user_conversations if conv['timestamp'] > week_ago])
        
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