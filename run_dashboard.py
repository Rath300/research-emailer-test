#!/usr/bin/env python3
"""
Cold Outreach AI Matchmaker - Web Dashboard Runner

Simple script to start the web dashboard with proper configuration.
"""

import os
import sys
import warnings
from pathlib import Path

# Suppress TensorFlow warnings that can cause hanging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore', category=UserWarning, module='tensorflow')
warnings.filterwarnings('ignore', category=FutureWarning, module='tensorflow')

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')

# Import and run the Flask app
try:
    from web_dashboard import app
    print("✅ Web dashboard imported successfully!")
except ImportError as e:
    print(f"❌ Error importing web dashboard: {e}")
    print("Please make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

if __name__ == '__main__':
    print("🚀 Starting Cold Outreach AI Matchmaker Dashboard...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to avoid import issues
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1) 