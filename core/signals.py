from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate, post_save
from django.db.utils import OperationalError, ProgrammingError
from django.dispatch import receiver
from django.utils import translation
from django.utils.translation import gettext

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
            if (
                issubclass(model, AbstractTranslatableCategory)
                and model is not AbstractTranslatableCategory
            ):
                if not model.objects.exists():
                    category = model.objects.create(title="Undefined", slug="undefined")

                    translation_model = None
                    for related in model._meta.related_objects:
                        rel_model = related.related_model
                        if (
                            issubclass(
                                rel_model, AbstractTranslatableCategoryTranslation
                            )
                            and rel_model is not AbstractTranslatableCategoryTranslation
                        ):
                            translation_model = rel_model
                            break

                    for lang_code, _ in settings.LANGUAGES:
                        with translation.override(lang_code):
                            title = gettext("Undefined")
                        translation_model.objects.create(
                            category=category,
                            language=lang_code,
                            title=title,
                        )

    except (OperationalError, ProgrammingError):
        pass


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
