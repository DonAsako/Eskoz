from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import migrations


def hash_existing_passwords(apps, schema_editor):
    Article = apps.get_model("blog", "Article")
    for article in Article.objects.exclude(password__isnull=True).exclude(password=""):
        try:
            identify_hasher(article.password)
        except ValueError:
            article.password = make_password(article.password)
            article.save(update_fields=["password"])


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_alter_article_password"),
    ]

    operations = [
        migrations.RunPython(hash_existing_passwords, migrations.RunPython.noop),
    ]
