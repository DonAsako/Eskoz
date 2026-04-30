from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import migrations


def hash_existing_passwords(apps, schema_editor):
    Writeup = apps.get_model("infosec", "Writeup")
    for writeup in Writeup.objects.exclude(password__isnull=True).exclude(password=""):
        try:
            identify_hasher(writeup.password)
        except ValueError:
            writeup.password = make_password(writeup.password)
            writeup.save(update_fields=["password"])


class Migration(migrations.Migration):

    dependencies = [
        ("infosec", "0002_alter_writeup_password"),
    ]

    operations = [
        migrations.RunPython(hash_existing_passwords, migrations.RunPython.noop),
    ]
