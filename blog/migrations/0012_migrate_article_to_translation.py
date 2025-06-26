from django.db import migrations


def migrate_article_data(apps, schema_editor):
    Article = apps.get_model("blog", "Article")
    ArticleTranslation = apps.get_model("blog", "ArticleTranslation")

    for article in Article.objects.all():
        ArticleTranslation.objects.create(
            article=article,
            language="en",
            title=article.title,
            description=article.description,
            content=article.content,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0011_create_articletranslation"),
    ]

    operations = [
        migrations.RunPython(migrate_article_data),
    ]
