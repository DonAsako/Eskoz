import os
import uuid

import markdown
from django.utils.safestring import mark_safe


def upload_to_random_filename(instance, filename, folder):
    ext = filename.split(".")[-1]
    random_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(folder, random_filename)


def upload_to_settings(instance, filename):
    return upload_to_random_filename(instance=instance, filename=filename, folder="settings")


def upload_to_projects(instance, filename):
    return upload_to_random_filename(instance=instance, filename=filename, folder="projects")


def upload_to_posts(instance, filename):
    return upload_to_random_filename(instance=instance, filename=filename, folder="posts")


def upload_to_certifications(instance, filename):
    return upload_to_random_filename(instance=instance, filename=filename, folder="certifications")


def upload_to_users(instance, filename):
    return upload_to_random_filename(instance=instance, filename=filename, folder="users")


def get_content_as_html(content):
    """
    Convert the Markdown content of the translatable markdown item to safe HTML.

    Returns:
        str: HTML representation of the post content.
    """
    html = markdown.markdown(
        content,
        extensions=[
            "extra",
            "codehilite",
            "fenced_code",
            "toc",
            "pymdownx.blocks.admonition",
            "pymdownx.arithmatex",
            "pymdownx.details",
            "pymdownx.superfences",
        ],
        extension_configs={
            "pymdownx.arithmatex": {
                "generic": True,
            },
            "pymdownx.blocks.admonition": {
                "types": [
                    "note",
                    "info",
                    "tip",
                    "success",
                    "warning",
                    "caution",
                    "danger",
                    "error",
                    "example",
                    "abstract",
                    "summary",
                    "tldr",
                    "quote",
                    "cite",
                    "question",
                    "faq",
                    "help",
                    "bug",
                    "security",
                    "flag",
                    "ctf",
                ]
            },
        },
    )
    return mark_safe(html)
