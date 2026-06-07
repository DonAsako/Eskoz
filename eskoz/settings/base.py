import os
from pathlib import Path

from django.conf.global_settings import LANGUAGES as DJANGO_LANGUAGES
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "auditlog",
    "apps.core",
    "apps.blog",
    "apps.infosec",
    "apps.education",
    "apps.analytics",
]


# django-unfold admin theme. Colours/sidebar refined in a later pass;
# kept minimal here so the default professional palette applies.
def _unfold_site_name(request):
    from apps.core.models import SiteSettings

    site_settings = SiteSettings.objects.first()
    return site_settings.site_name if site_settings and site_settings.site_name else "Eskoz"


def _unfold_site_subheader(request):
    from eskoz import __version__

    return f"v{__version__}"


def _unfold_favicons(request):
    from apps.core.models import SiteSettings

    site_settings = SiteSettings.objects.first()
    if site_settings and site_settings.favicon:
        return [{"rel": "icon", "href": site_settings.favicon.url}]
    return []


UNFOLD = {
    "SITE_TITLE": _unfold_site_name,
    "SITE_HEADER": _unfold_site_name,
    "SITE_SUBHEADER": _unfold_site_subheader,
    "SITE_FAVICONS": _unfold_favicons,
    "SITE_URL": "/",
    "DASHBOARD_CALLBACK": "apps.core.dashboard.dashboard_callback",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "BORDER_RADIUS": "6px",
    "COLORS": {
        "primary": {
            "50": "oklch(97.5% 0.013 236.0)",
            "100": "oklch(95.1% 0.028 236.5)",
            "200": "oklch(90.2% 0.056 237.0)",
            "300": "oklch(83.5% 0.104 234.3)",
            "400": "oklch(74.4% 0.171 231.9)",
            "500": "oklch(62.9% 0.236 259.1)",
            "600": "oklch(54.6% 0.246 262.9)",
            "700": "oklch(47.7% 0.222 261.5)",
            "800": "oklch(40.0% 0.177 260.7)",
            "900": "oklch(34.5% 0.138 261.3)",
            "950": "oklch(25.6% 0.105 261.7)",
        },
    },
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("General"),
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": _("Analytics"),
                        "icon": "monitoring",
                        "link": reverse_lazy("admin:analytics"),
                    },
                ],
            },
            {
                "title": _("Blog"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Articles"), "icon": "article", "link": reverse_lazy("admin:blog_article_changelist")},
                    {
                        "title": _("Projects"),
                        "icon": "rocket_launch",
                        "link": reverse_lazy("admin:blog_project_changelist"),
                    },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:blog_category_changelist"),
                    },
                    {"title": _("Tags"), "icon": "label", "link": reverse_lazy("admin:blog_articletag_changelist")},
                ],
            },
            {
                "title": _("Infosec"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Writeups"), "icon": "flag", "link": reverse_lazy("admin:infosec_writeup_changelist")},
                    {"title": _("CTF"), "icon": "emoji_events", "link": reverse_lazy("admin:infosec_ctf_changelist")},
                    {"title": _("CVE"), "icon": "bug_report", "link": reverse_lazy("admin:infosec_cve_changelist")},
                    {
                        "title": _("Certifications"),
                        "icon": "workspace_premium",
                        "link": reverse_lazy("admin:infosec_certification_changelist"),
                    },
                    {
                        "title": _("Issuers"),
                        "icon": "business",
                        "link": reverse_lazy("admin:infosec_issuer_changelist"),
                    },
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:infosec_category_changelist"),
                    },
                    {"title": _("Tags"), "icon": "label", "link": reverse_lazy("admin:infosec_writeuptag_changelist")},
                ],
            },
            {
                "title": _("Education"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Courses"),
                        "icon": "school",
                        "link": reverse_lazy("admin:education_course_changelist"),
                    },
                    {
                        "title": _("Modules"),
                        "icon": "layers",
                        "link": reverse_lazy("admin:education_module_changelist"),
                    },
                    {"title": _("Lessons"), "icon": "book", "link": reverse_lazy("admin:education_lesson_changelist")},
                    {
                        "title": _("Categories"),
                        "icon": "category",
                        "link": reverse_lazy("admin:education_category_changelist"),
                    },
                ],
            },
            {
                "title": _("Team"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {"title": _("Users"), "icon": "group", "link": reverse_lazy("admin:auth_user_changelist")},
                    {
                        "title": _("Groups"),
                        "icon": "manage_accounts",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
            {
                "title": _("Settings"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Site Settings"),
                        "icon": "settings",
                        "link": reverse_lazy("admin:core_sitesettings_changelist"),
                    },
                    {"title": _("Pages"), "icon": "web", "link": reverse_lazy("admin:core_page_changelist")},
                ],
            },
        ],
    },
    "TABS": [
        # CTF-related content
        {
            "models": ["infosec.writeup", "infosec.ctf"],
            "items": [
                {"title": _("Writeups"), "link": reverse_lazy("admin:infosec_writeup_changelist")},
                {"title": _("CTF"), "link": reverse_lazy("admin:infosec_ctf_changelist")},
            ],
        },
        # Blog content
        {
            "models": ["blog.article", "blog.project"],
            "items": [
                {"title": _("Articles"), "link": reverse_lazy("admin:blog_article_changelist")},
                {"title": _("Projects"), "link": reverse_lazy("admin:blog_project_changelist")},
            ],
        },
        # Certifications & Issuers
        {
            "models": ["infosec.certification", "infosec.issuer"],
            "items": [
                {"title": _("Certifications"), "link": reverse_lazy("admin:infosec_certification_changelist")},
                {"title": _("Issuers"), "link": reverse_lazy("admin:infosec_issuer_changelist")},
            ],
        },
        # Blog taxonomy
        {
            "models": ["blog.category", "blog.articletag", "blog.projecttag"],
            "items": [
                {"title": _("Categories"), "link": reverse_lazy("admin:blog_category_changelist")},
                {"title": _("Article Tags"), "link": reverse_lazy("admin:blog_articletag_changelist")},
                {"title": _("Project Tags"), "link": reverse_lazy("admin:blog_projecttag_changelist")},
            ],
        },
        # Infosec taxonomy
        {
            "models": ["infosec.category", "infosec.writeuptag"],
            "items": [
                {"title": _("Categories"), "link": reverse_lazy("admin:infosec_category_changelist")},
                {"title": _("Tags"), "link": reverse_lazy("admin:infosec_writeuptag_changelist")},
            ],
        },
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "apps.core.middleware.LegacyURLPermanentRedirectMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "apps.core.middleware.AdminDefaultLanguageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.Force2FAMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_ratelimit.middleware.RatelimitMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    "apps.core.middleware.ActiveThemeMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
    "apps.analytics.middleware.PageViewMiddleware",
]

ROOT_URLCONF = "eskoz.urls"

# Security hardening — applied in every environment.
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True

# Cross-process cache backing django-ratelimit counters. DB-backed so a
# single Postgres/SQLite holds the truth across all gunicorn workers
# without requiring Redis. Run `manage.py createcachetable` once.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}

# Rate-limit policy for the admin login + 2FA management endpoints.
RATELIMIT_LOGIN_IP = "10/15m"
RATELIMIT_LOGIN_USERNAME = "5/15m"
RATELIMIT_2FA_IP = "10/15m"
RATELIMIT_VIEW = "apps.core.views.ratelimited"

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
                "apps.core.context_processors.pagination",
                "apps.core.context_processors.languages",
                "apps.core.context_processors.seo",
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

# Open the language universe to every locale Django ships with (~100 codes).
# This means:
#   - admins can write a Translation in any language, no hardcoded allow-list
#   - URL routing accepts /<any-lang>/... but the post-detail fallback will
#     301 to the default language when no translation exists
#   - the navbar switcher does NOT iterate this list — it's bound to the
#     languages that have actual content in DB (see context_processors)
LANGUAGES = DJANGO_LANGUAGES

# Default site language. Drives:
#   - The URL prefix served when no language is in the path (e.g. /fr/articles/...)
#   - The 301 target when a translation is missing in the requested language
#   - The admin back-office language
# Editable via `python manage.py config` (LANGUAGE_CODE in .env).
LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "fr")

# Hard-fail at startup if the configured default isn't a real Django locale
# code, otherwise i18n_patterns would silently route requests to "en".
_LANG_CODES = {code for code, _label in LANGUAGES}
if LANGUAGE_CODE not in _LANG_CODES:
    raise ValueError(f"LANGUAGE_CODE={LANGUAGE_CODE!r} is not a valid Django language code")

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = True

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

POSTS_PER_PAGE = 12
POSTS_PER_PAGE_CHOICES = [12, 24, 36]

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
