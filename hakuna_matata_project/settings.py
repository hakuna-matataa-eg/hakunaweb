# settings.py

from pathlib import Path
import os
from decouple import config
import dj_database_url

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# --- إعدادات حساسة من .env ---
SECRET_KEY = config('SECRET_KEY')

# ==================== التعديل الأهم ====================
# قمنا بتثبيت قيمة DEBUG على True لبيئة التطوير المحلية
DEBUG = True
# ======================================================

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost,staging.hakuna-matataa.com', # تمت إضافة نطاق التطوير
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# --- التطبيقات ---
INSTALLED_APPS = [
    'tours',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
]

# --- الوسيطات ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- إعدادات التوجيه ---
ROOT_URLCONF = 'hakuna_matata_project.urls'

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
                'django.contrib.messages.context_processors.messages', # This is the corrected line
                'tours.context_processors.booking_form_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'hakuna_matata_project.wsgi.application'

# --- إعداد قاعدة البيانات ---
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

# --- التحقق من كلمات المرور ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- اللغة والتوقيت ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- إعدادات الملفات الثابتة والميديا ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # للإنتاج فقط

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==================== التعديل الثاني ====================
# هذا هو المسار الصحيح الذي سيبحث فيه جانغو عن ملفاتك الثابتة
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
# ======================================================

# --- إعدادات CKEditor ---
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'