from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.contrib.auth.signals import user_logged_in
from django.core.cache import cache
from django.db.models.signals import post_delete, post_migrate, post_save
from django.db.utils import OperationalError, ProgrammingError
from django.dispatch import receiver
from django.utils import translation
from django.utils.translation import gettext

from apps.core.context_processors import ACTIVE_LANGUAGES_CACHE_KEY

from .models import (
    AbstractTranslatableCategory,
    AbstractTranslatableCategoryTranslation,
    BlogSettings,
    EducationSettings,
    InfosecSettings,
    SeoSettings,
    SiteSettings,
    UserProfile,
)


# Create SiteSettings on start
@receiver(post_migrate)
def create_site_settings(sender, **kwargs):
    try:
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(site_name="Eskoz")
    except (OperationalError, ProgrammingError):
        pass


@receiver(post_migrate)
def create_undefined_categories(sender, **kwargs):
    try:
        for model in apps.get_models():
            if issubclass(model, AbstractTranslatableCategory) and model is not AbstractTranslatableCategory:
                if not model.objects.exists():
                    category = model.objects.create(title="Undefined", slug="undefined")

                    translation_model = None
                    for related in model._meta.related_objects:
                        rel_model = related.related_model
                        if (
                            issubclass(rel_model, AbstractTranslatableCategoryTranslation)
                            and rel_model is not AbstractTranslatableCategoryTranslation
                        ):
                            translation_model = rel_model
                            break

                    # Seed only the configured default language. The site
                    # supports the full Django LANGUAGES universe but it
                    # would be wasteful to create ~100 placeholder rows
                    # per category on a fresh install.
                    lang_code = settings.LANGUAGE_CODE
                    with translation.override(lang_code):
                        title = gettext("Undefined")
                    translation_model.objects.create(
                        category=category,
                        language=lang_code,
                        title=title,
                    )

    except (OperationalError, ProgrammingError):
        pass


@receiver(post_migrate)
def create_editor_group(sender, **kwargs):
    editor, _ = Group.objects.get_or_create(name="Editor")
    permissions = []

    for app_label, config in settings.EDITOR_PERMISSIONS.items():
        for model in config["models"]:
            for action in config["actions"]:
                try:
                    perm = Permission.objects.get(
                        codename=f"{action}_{model}",
                        content_type__app_label=app_label,
                    )
                    permissions.append(perm)
                except Permission.DoesNotExist:
                    pass
    editor.permissions.set(permissions)


@receiver(post_save, sender=SiteSettings)
def create_related_settings(sender, instance, **kwargs):
    SeoSettings.objects.get_or_create(site_settings=instance)
    InfosecSettings.objects.get_or_create(site_settings=instance)
    BlogSettings.objects.get_or_create(site_settings=instance)
    EducationSettings.objects.get_or_create(site_settings=instance)


# Create UserProfile on creation of User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(user_logged_in)
def reset_2fa_verified_flag(sender, request, user, **kwargs):
    """Force every fresh login through the 2FA gate again.

    Without this, a stale ``2fa_verified=True`` from a previous session
    could (in theory) survive ``cycle_key`` on anon → auth and bypass the
    second factor.
    """
    if request and hasattr(request, "session"):
        request.session.pop("2fa_verified", None)


def _bust_active_language_cache(sender, **kwargs):
    """Drop the cached language list whenever a Translation row changes.

    Subscribed lazily inside ready() so we can iterate the concrete
    Translation models without import-cycling against this module.
    """
    cache.delete(ACTIVE_LANGUAGES_CACHE_KEY)


def register_translation_cache_invalidators():
    """Wire post_save/post_delete on every concrete *Translation model."""
    from apps.blog.models import ArticleTranslation
    from apps.blog.models import CategoryTranslation as BlogCategoryTranslation
    from apps.education.models import CategoryTranslation as EducationCategoryTranslation
    from apps.education.models import LessonTranslation
    from apps.infosec.models import CategoryTranslation as InfosecCategoryTranslation
    from apps.infosec.models import WriteupTranslation

    for model in (
        ArticleTranslation,
        WriteupTranslation,
        LessonTranslation,
        BlogCategoryTranslation,
        InfosecCategoryTranslation,
        EducationCategoryTranslation,
    ):
        post_save.connect(_bust_active_language_cache, sender=model, weak=False)
        post_delete.connect(_bust_active_language_cache, sender=model, weak=False)


register_translation_cache_invalidators()
