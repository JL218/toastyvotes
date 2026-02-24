"""
WSGI config for PythonAnywhere deployment.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the Python path
# Adjust this path to match your PythonAnywhere setup
PROJECT_DIR = Path('/home/toastyvotes')
sys.path.insert(0, str(PROJECT_DIR))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toastyvotes.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
