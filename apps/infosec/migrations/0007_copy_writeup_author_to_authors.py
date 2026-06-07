from django.db import migrations


def copy_author_to_authors(apps, schema_editor):
    Writeup = apps.get_model("infosec", "Writeup")
    for writeup in Writeup.objects.filter(author__isnull=False):
        writeup.authors.add(writeup.author_id)


def copy_authors_to_author(apps, schema_editor):
    Writeup = apps.get_model("infosec", "Writeup")
    for writeup in Writeup.objects.all():
        first = writeup.authors.first()
        if first is not None:
            writeup.author_id = first.pk
            writeup.save(update_fields=["author"])


class Migration(migrations.Migration):
    dependencies = [
        ("infosec", "0006_writeup_authors"),
    ]

    operations = [
        migrations.RunPython(copy_author_to_authors, copy_authors_to_author),
    ]
