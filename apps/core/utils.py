import os
import uuid

import markdown
import nh3
from django.utils.safestring import mark_safe

_ALLOWED_TAGS = nh3.ALLOWED_TAGS | {
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "pre",
    "details",
    "summary",
    "div",
    "span",
    "del",
    "ins",
    "sub",
    "sup",
    "kbd",
    "mark",
    "section",
    "figure",
    "figcaption",
    "caption",
    "table",
    "thead",
    "tbody",
    "tfoot",
    "tr",
    "th",
    "td",
    "col",
    "colgroup",
    "dl",
    "dt",
    "dd",
}

_CLASS_ID_TAGS = {
    "a",
    "p",
    "pre",
    "code",
    "span",
    "div",
    "details",
    "summary",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "blockquote",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "ul",
    "ol",
    "li",
    "section",
}
_ALLOWED_ATTRIBUTES = {tag: set(attrs) for tag, attrs in nh3.ALLOWED_ATTRIBUTES.items()}
for _tag in _CLASS_ID_TAGS:
    _ALLOWED_ATTRIBUTES.setdefault(_tag, set()).update({"class", "id"})
_ALLOWED_ATTRIBUTES.setdefault("a", set()).update({"href", "title"})
_ALLOWED_ATTRIBUTES.setdefault("img", set()).update({"src", "alt", "title"})
_ALLOWED_ATTRIBUTES.setdefault("details", set()).add("open")
_ALLOWED_ATTRIBUTES.setdefault("ol", set()).add("start")
_ALLOWED_ATTRIBUTES.setdefault("td", set()).update({"colspan", "rowspan"})
_ALLOWED_ATTRIBUTES.setdefault("th", set()).update({"colspan", "rowspan"})
_ALLOWED_ATTRIBUTES.setdefault("abbr", set()).add("title")


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
            "fenced_code",
            "toc",
            "pymdownx.blocks.admonition",
            "pymdownx.arithmatex",
            "pymdownx.details",
            "pymdownx.superfences",
            "pymdownx.highlight",
        ],
        extension_configs={
            # Disable server-side Pygments — hljs (loaded on the page)
            # owns syntax highlighting, and use_pygments=False makes
            # superfences emit `<code class="language-X">` so both hljs
            # and the theme JS topbar can read the language.
            "pymdownx.highlight": {
                "use_pygments": False,
            },
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
    # Safe: the HTML is sanitized by nh3.clean() on the same line before mark_safe.
    return mark_safe(nh3.clean(html, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRIBUTES))  # noqa: S308
