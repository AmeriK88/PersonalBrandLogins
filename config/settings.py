from pathlib import Path
import environ

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static



BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR / '.env')

env = environ.Env(
    DEBUG=(bool, False),
)

SECRET_KEY = env('SECRET_KEY')


ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')


# Application definition

INSTALLED_APPS = [
    'unfold',                       
    'unfold.contrib.filters',   
    'unfold.contrib.forms',  
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Installed apps
    "core",
    'career',
    'highlights',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

# ========== EMAIL CONFIG BY ENVIRONMENT ==========
ENVIRONMENT = env("ENVIRONMENT", default="development")

if ENVIRONMENT == "production":
    # Producción: usar Gmail + App Password
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = env.int("EMAIL_PORT", default=587)
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)

    EMAIL_HOST_USER = env("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env("PASSWORD_APP")
else:
    # Desarrollo: emails a la consola (no hay TLS, no hay Gmail)
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@gregloginsjr.com")




# UNFOLD Admin Panel Config
UNFOLD = {
    # Básico de branding
    "SITE_TITLE": "Greg´s Admin",
    "SITE_HEADER": "Greg´s Admin Panel",
    "SITE_SUBHEADER": "Player & Content Management",
    "SITE_URL": "/",

    # Icons / logos 
    "SITE_ICON": {
        "light": lambda request: static("img/admin/icon-dark.svg"),
        "dark": lambda request: static("img/admin/icon-light.svg"),
    },
    "SITE_LOGO": {
        "light": lambda request: static("img/admin/logo-light.webp"),
        "dark": lambda request: static("img/admin/logo-dark.webp"),
    },
    "SITE_SYMBOL": "sports_basketball",  

        "STYLES": [
        lambda request: static("css/admin_overrides.css"),
    ],

    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("img/admin/icon-light.svg"),
        },
    
    ],

    #  UX del admin
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": False,
    #"THEME": "dark",
    "DARK_MODE": True, 

    # Login
    "LOGIN": {
        "image": lambda request: static("img/admin/login-bg.svg"),
        "redirect_after": lambda request: reverse_lazy("admin:blog_post_changelist"),
    },

    # Colors
    "COLORS": {
        "primary": {
            "50":  "239, 246, 255",
            "100": "219, 234, 254",
            "200": "191, 219, 254",
            "300": "147, 197, 253",
            "400": "96, 165, 250",
            "500": "59, 130, 246", 
            "600": "37, 99, 235",
            "700": "29, 78, 216",
            "800": "30, 64, 175",
            "900": "30, 58, 138",
            "950": "23, 37, 84",
        }
    },

    # Sidebar / Nav
    "SIDEBAR": {
        "show_search": True,
        "command_search": False,
        "show_all_applications": True,

        "navigation": [
            {
                "title": _("Main"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Content"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Blog posts"),
                        "icon": "article",
                        "link": reverse_lazy("admin:blog_post_changelist"),
                    },
                    {
                        "title": _("Career experience"),
                        "icon": "flag",
                        "link": reverse_lazy("admin:career_experience_changelist"),
                    },
                    {
                        "title": _("Highlights"),
                        "icon": "movie",
                        "link": reverse_lazy("admin:highlights_highlight_changelist"),
                    },
                ],
            },
            {
                "title": _("Users & Access"),
                "collapsible": True,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                ],
            },
        ],
    },

}



# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
