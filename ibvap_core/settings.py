"""
Django settings for IBVAP project.
Intelligent Border Video Analytics Platform (SIH Prototype - Phase 1)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-ibvap-sih-border-intelligence-prototype-key-2026'
)

DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Application definition
INSTALLED_APPS = [
    # Django Unfold (Must be placed before django.contrib.admin)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    
    # Local Apps
    'apps.accounts',
    'apps.dashboard',
    'apps.cameras',
    'apps.alerts',
    'apps.events',
    'apps.anpr',
    'apps.watchlist',
    'apps.map',
    'apps.analytics',
    'apps.settings_app',
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ibvap_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.global_system_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'ibvap_core.wsgi.application'
ASGI_APPLICATION = 'ibvap_core.asgi.application'

# Database configuration
# Uses SQLite3 locally by default; if DATABASE_URL is set (e.g. PostgreSQL on Render), it seamlessly switches.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

database_url = os.getenv('DATABASE_URL')
if database_url:
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    except Exception as e:
        print(f"Warning: Could not configure DATABASE_URL: {e}. Falling back to SQLite3.")

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise compression & caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'accounts:login'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Django Unfold Configuration
UNFOLD = {
    'SITE_TITLE': 'IBVAP Command Admin',
    'SITE_HEADER': 'IBVAP | Intelligent Border Video Analytics',
    'SITE_SUBHEADER': 'HQ Surveillance & Threat Intelligence Operations',
    'SITE_SYMBOL': 'shield',
    'SITE_URL': '/',
    'ENVIRONMENT': 'IBVAP.HQ // LIVE BORDER SEC-OPS',
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': True,
    'DASHBOARD_CALLBACK': 'apps.core.admin_dashboard.dashboard_callback',
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': True,
        'navigation': [
            {
                'title': _('Border Surveillance'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': _('Camera Feeds'),
                        'icon': 'videocam',
                        'link': reverse_lazy('admin:cameras_camera_changelist'),
                    },
                    {
                        'title': _('Security Alerts'),
                        'icon': 'warning',
                        'link': reverse_lazy('admin:alerts_securityalert_changelist'),
                    },
                    {
                        'title': _('Security Events'),
                        'icon': 'event_note',
                        'link': reverse_lazy('admin:events_securityevent_changelist'),
                    },
                ],
            },
            {
                'title': _('Vehicle Intel & ANPR'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': _('ANPR Detections'),
                        'icon': 'directions_car',
                        'link': reverse_lazy('admin:anpr_anprdetection_changelist'),
                    },
                    {
                        'title': _('Watchlist Vehicles'),
                        'icon': 'radar',
                        'link': reverse_lazy('admin:watchlist_watchlistvehicle_changelist'),
                    },
                ],
            },
            {
                'title': _('System & Access Management'),
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': _('System Configuration'),
                        'icon': 'tune',
                        'link': reverse_lazy('admin:settings_app_systemconfiguration_changelist'),
                    },
                    {
                        'title': _('Officer Profiles'),
                        'icon': 'badge',
                        'link': reverse_lazy('admin:accounts_userprofile_changelist'),
                    },
                    {
                        'title': _('User Accounts'),
                        'icon': 'person',
                        'link': reverse_lazy('admin:auth_user_changelist'),
                    },
                    {
                        'title': _('User Groups'),
                        'icon': 'group',
                        'link': reverse_lazy('admin:auth_group_changelist'),
                    },
                ],
            },
            {
                'title': _('Live Operations Portals'),
                'separator': True,
                'collapsible': False,
                'items': [
                    {
                        'title': _('HQ Live Dashboard'),
                        'icon': 'dashboard',
                        'link': reverse_lazy('dashboard:index'),
                    },
                    {
                        'title': _('Camera Grid'),
                        'icon': 'grid_view',
                        'link': reverse_lazy('cameras:list'),
                    },
                    {
                        'title': _('Tactical Sector Map'),
                        'icon': 'map',
                        'link': reverse_lazy('map:index'),
                    },
                    {
                        'title': _('Threat Analytics'),
                        'icon': 'analytics',
                        'link': reverse_lazy('analytics:index'),
                    },
                ],
            },
        ],
    },
}
