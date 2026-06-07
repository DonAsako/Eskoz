from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_userprofile_github_userprofile_role_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="blogsettings",
            old_name="activate_members_view",
            new_name="activate_members_page",
        ),
    ]
