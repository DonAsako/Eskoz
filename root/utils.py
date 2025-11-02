import uuid
import os


def upload_to_random_filename(instance, filename, folder):
    ext = filename.split(".")[-1]
    random_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(folder, random_filename)


def upload_to_settings(instance, filename):
    return upload_to_random_filename(
        instance=instance, filename=filename, folder="settings"
    )


def upload_to_projects(instance, filename):
    return upload_to_random_filename(
        instance=instance, filename=filename, folder="projects"
    )


def upload_to_posts(instance, filename):
    return upload_to_random_filename(
        instance=instance, filename=filename, folder="posts"
    )


def upload_to_certifications(instance, filename):
    return upload_to_random_filename(
        instance=instance, filename=filename, folder="certifications"
    )


def upload_to_users(instance, filename):
    return upload_to_random_filename(
        instance=instance, filename=filename, folder="users"
    )
