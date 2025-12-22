import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core",
    "apps.blog",
    "apps.infosec",
    "apps.education",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.ActiveThemeMiddleware",
]

ROOT_URLCONF = "eskoz.urls"

ACTIVE_THEME = os.getenv("THEME", "Eskoz")


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "themes", ACTIVE_THEME, "templates"),
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
                "apps.core.context_processors.active_theme",
            ],
        },
    },
]


WSGI_APPLICATION = "eskoz.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
    ("it", _("Italian")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static", BASE_DIR / "themes" / ACTIVE_THEME / "static"]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ADMIN_URL = os.getenv("ADMIN_URL") or "admin"

EDITOR_PERMISSIONS = {
    "infosec": {
        "models": [
            "ctf",
            "category",
            "categorytranslation",
            "certification",
            "cve",
            "issuer",
            "tag",
            "writeup",
            "writeuptag",
            "writeuptranslation",
        ],
        "actions": ("add", "change", "view", "delete"),
    },
    "blog": {
        "models": [
            "article",
            "articletranslation",
            "articletag",
            "category",
            "categorytranslation",
            "project",
            "projecttag",
        ],
        "actions": ("add", "change", "view", "delete"),
    },
    "education": {
        "models": [
            "category",
            "categorytranslation",
            "course",
            "module",
            "lesson",
            "lessontranslation",
        ],
        "actions": ("add", "change", "view"),
    },
    "core": {
        "models": [
            "page",
            "sitesettings",
            "seosettings",
            "wellknownfile",
            "blogsettings",
            "infosecsettings",
            "educationsettings",
            "translatablemarkdownitemimage",
        ],
        "actions": ("view", "add", "delete"),
    },
}
