import os
import sys
import importlib.util
from pathlib import Path

# Add the project directory to the Python path
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toastyvotes.settings')

# Import Django WSGI application
spec = importlib.util.spec_from_file_location(
    "application", 
    os.path.join(CURRENT_DIR, "toastyvotes", "wsgi.py")
)
wsgi_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wsgi_module)
application = wsgi_module.application
