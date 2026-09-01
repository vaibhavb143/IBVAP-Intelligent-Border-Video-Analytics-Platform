"""
ASGI config for IBVAP project.
WebSocket and Real-time ready.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ibvap_core.settings')

application = get_asgi_application()
