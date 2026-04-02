from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Tracks meaningful user actions across the system.
    Intentionally simple — no signals, no magic.
    The log_action() helper is called explicitly in views.
    """

    ACTION_CHOICES = [
        # Define your action types here, e.g.:
        #('CREATE', 'Create'), etc
    ]

    """Add fields as needed, e.g. timestamp, user, action type, model name, object id, changes, etc."""

    