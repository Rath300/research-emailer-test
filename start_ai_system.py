#!/usr/bin/env python3
"""
Clean startup script for AI Cold Outreach System
Suppresses all warnings and starts the system properly
"""

import os
import sys
import warnings

# Suppress ALL warnings before any imports
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'

# Suppress TensorFlow warnings specifically
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

# Now import and start the system
from simple_dashboard import app

if __name__ == '__main__':
    print("🤖 Starting AI-Powered Cold Outreach System...")
    print("🧠 AI Mode: DEMO (Mock AI Agents)")
    print("💡 To enable real AI: Set OPENAI_API_KEY and USE_REAL_AI=true")
    print("📱 Open your browser: http://localhost:5001")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=False)  # debug=False to reduce warnings
    except KeyboardInterrupt:
        print("\n✅ AI System stopped successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Try: pip install flask flask-wtf wtforms") 