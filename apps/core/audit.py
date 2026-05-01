"""Audit-log registration for sensitive admin models.

Tracked here so any change made through the admin (or any ORM call) is
recorded with the acting user, the diff, and a timestamp. View the entries
under ``/admin/auditlog/logentry/``.
"""

from auditlog.registry import auditlog
from django.contrib.auth.models import User

from apps.blog.models import Article, Project
from apps.core.models import Page, SiteSettings, User2FA, UserLink, UserProfile
from apps.education.models import Course, Lesson, Module
from apps.infosec.models import CTF, CVE, Certification, Writeup

# Auth & site config — the highest-value audit trail.
auditlog.register(User, exclude_fields=["last_login"])
auditlog.register(User2FA, exclude_fields=["secret_key", "backup_codes"])
auditlog.register(UserProfile)
auditlog.register(UserLink)
auditlog.register(SiteSettings)

# Content models — we want to know who edited / unpublished what and when.
auditlog.register(Page)
auditlog.register(Article)
auditlog.register(Project)
auditlog.register(Writeup)
auditlog.register(Lesson)
auditlog.register(Module)
auditlog.register(Course)
auditlog.register(Certification)
auditlog.register(CVE)
auditlog.register(CTF)
