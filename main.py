import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from memory import memory_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ora-memory-secret-key-2024'

# Enable CORS for all routes
CORS(app)

# Register memory routes
app.register_blueprint(memory_bp, url_prefix='/api/memory')

# Initialize JSON data file
def init_data():
    """Initialize JSON data file with required structure"""
    data_file = os.path.join(os.path.dirname(__file__), 'ora_memory.json')
    
    if not os.path.exists(data_file):
        initial_data = {
            'users': {},
            'conversations': []
        }
        with open(data_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
        print(f"✅ Data file initialized: {data_file}")
    else:
        print(f"✅ Data file exists: {data_file}")

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'ORA Memory API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

# Root endpoint
@app.route('/')
def root():
    return jsonify({
        'message': 'ORA Memory API is running! 🧠✨',
        'endpoints': {
            'health': '/health',
            'admin_panel': '/admin',
            'get_user_context': '/api/memory/get-context',
            'save_conversation': '/api/memory/save-conversation',
            'update_profile': '/api/memory/update-profile',
            'get_user_stats': '/api/memory/get-stats',
            'get_all_users': '/api/memory/get-all-users',
            'search_conversations': '/api/memory/search-conversations'
        },
        'documentation': 'Send POST requests to the memory endpoints'
    })

# Admin panel route
@app.route('/admin')
def admin_panel():
    """Serve the admin panel HTML"""
    return send_from_directory('.', 'admin.html')

if __name__ == '__main__':
    # Initialize data file on startup
    init_data()
    
    print("🚀 Starting ORA Memory API...")
    print("📊 Database: JSON File Storage")
    print("🧠 Memory: Enabled")
    print("🎯 Admin Panel: Available at /admin")
    print("🌐 CORS: Enabled")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)