# Generated by Django 5.2.1 on 2025-07-19 20:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("root", "0014_remove_theme_theme_type"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Theme",
        ),
    ]
