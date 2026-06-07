from django.db import migrations


def copy_author_to_authors(apps, schema_editor):
    CVE = apps.get_model("infosec", "CVE")
    for cve in CVE.objects.filter(author__isnull=False):
        cve.authors.add(cve.author_id)


def copy_authors_to_author(apps, schema_editor):
    CVE = apps.get_model("infosec", "CVE")
    for cve in CVE.objects.all():
        first = cve.authors.first()
        if first is not None:
            cve.author_id = first.pk
            cve.save(update_fields=["author"])


class Migration(migrations.Migration):
    dependencies = [
        ("infosec", "0009_cve_authors"),
    ]

    operations = [
        migrations.RunPython(copy_author_to_authors, copy_authors_to_author),
    ]
