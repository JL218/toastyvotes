"""
WSGI config for toastyvotes project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Add the project path to the Python path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

# Load environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toastyvotes.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
