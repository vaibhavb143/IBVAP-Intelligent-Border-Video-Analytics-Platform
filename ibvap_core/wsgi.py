"""
WSGI config for IBVAP project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ibvap_core.settings')

application = get_wsgi_application()
