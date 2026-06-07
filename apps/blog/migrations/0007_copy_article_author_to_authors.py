from django.db import migrations


def copy_author_to_authors(apps, schema_editor):
    Article = apps.get_model("blog", "Article")
    for article in Article.objects.filter(author__isnull=False):
        article.authors.add(article.author_id)


def copy_authors_to_author(apps, schema_editor):
    Article = apps.get_model("blog", "Article")
    for article in Article.objects.all():
        first = article.authors.first()
        if first is not None:
            article.author_id = first.pk
            article.save(update_fields=["author"])


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0006_article_authors"),
    ]

    operations = [
        migrations.RunPython(copy_author_to_authors, copy_authors_to_author),
    ]
