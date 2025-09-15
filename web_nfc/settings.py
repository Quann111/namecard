import os
from pathlib import Path
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "changeme-in-local")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() == "false"

# Hosts
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "127.0.0.1 localhost [::1]").split()

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary",
    "cloudinary_storage",
    "members",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # phục vụ static trong production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "web_nfc.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # custom templates
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",   # ✅ thêm dòng này

            ],
        },
    },
]

WSGI_APPLICATION = "web_nfc.wsgi.application"

# Database default = SQLite, nếu có DATABASE_URL thì override
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("DB_NAME", "webnfc"),
        'USER': os.environ.get("DB_USER", "webnfc_user"),
        'PASSWORD': os.environ.get("DB_PASSWORD", "1t74n3mnc4Fkqs70pY3CZtG78o9TH0fw"),
        'HOST': os.environ.get("DB_HOST", "dpg-d300hcvdiees738rf8rg-a.frankfurt-postgres.render.com"),
        'PORT': os.environ.get("DB_PORT", "5432"),
    }
}
database_url = os.environ.get("DATABASE_URL")
if database_url:
    DATABASES["default"] = dj_database_url.parse(database_url)

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "productionfiles"  # nơi collectstatic gom vào

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Cloudinary Storage config
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Cloudinary từ biến môi trường (production)
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", "dyknreycq"),
    api_key=os.environ.get("CLOUDINARY_API_KEY", "821838178795467"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "6JK85cCavtF4TVSgJRguuWogNx8"),
    secure=True
)

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
