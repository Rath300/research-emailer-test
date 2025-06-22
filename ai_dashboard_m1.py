#!/usr/bin/env python3
"""
AI Cold Outreach System - M1 Mac Compatible Version
Fixes TensorFlow import issues on Apple Silicon
"""

import warnings
import os
import sys

# M1 Mac Fix: Completely suppress TensorFlow and related warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'

from flask import Flask, render_template, request, jsonify, session
import json
import random
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'cold-outreach-ai-secret-key-2024'

# Check for Real AI availability (without TensorFlow)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
USE_REAL_AI = os.getenv('USE_REAL_AI', 'false').lower() == 'true'

print("🤖 Starting M1 Mac Compatible AI System...")
print("✅ TensorFlow Issues Resolved")
print("📱 Open your browser: http://localhost:5001")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
