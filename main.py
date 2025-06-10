import os
import sys
import sqlite3
from datetime import datetime
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from src.routes.memory import memory_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'ora-memory-secret-key-2024'

# Register memory routes
app.register_blueprint(memory_bp, url_prefix='/api/memory')

# Initialize SQLite database
def init_db():
    """Initialize SQLite database with required tables"""
    db_path = os.path.join(os.path.dirname(__file__), 'ora_memory.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            personality_type TEXT,
            communication_style TEXT,
            first_visit TIMESTAMP,
            last_visit TIMESTAMP,
            onboarding_complete BOOLEAN DEFAULT 0,
            preferences TEXT,
            total_conversations INTEGER DEFAULT 0
        )
    ''')
    
    # Conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp TIMESTAMP,
            user_message TEXT,
            ora_response TEXT,
            emotion TEXT,
            topic TEXT,
            session_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # User insights table (for behavioral patterns)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            insight_type TEXT,
            insight_value TEXT,
            confidence_score REAL,
            created_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {db_path}")

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
            'get_user_stats': '/api/memory/get-stats'
        },
        'documentation': 'Send POST requests to the memory endpoints'
    })

# Admin panel route
@app.route('/admin')
def admin_panel():
    """Serve the admin panel HTML"""
    return app.send_static_file('admin.html')

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    print("🚀 Starting ORA Memory API...")
    print("📊 Database: SQLite")
    print("🧠 Memory: Enabled")
    print("🔗 Ready for Make.com integration!")
    print("🎯 Admin Panel: Available at /admin")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

