from django.contrib.auth.models import AbstractUser
from django.db import models
 
 
class User(AbstractUser):
    """
    Custom user model. Role is stored directly on the user for fast
    permission checks without hitting the groups table on every request.
    """
 
    class Role(models.TextChoices):
        ADMIN      = 'admin',      'Admin'
        SUPERVISOR = 'supervisor', 'Supervisor'
        MANAGER    = 'manager',    'Manager'
        VIEWER     = 'viewer',     'Viewer'
        READER     = 'reader',     'Reader'
 
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.READER,
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
    )
 
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']
 
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
 
    # --- Role shortcuts ---------------------------------------------------
 
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
 
    @property
    def is_supervisor(self):
        return self.role in (self.Role.ADMIN, self.Role.SUPERVISOR) or self.is_superuser
 
    @property
    def is_manager(self):
        return self.role in (
            self.Role.ADMIN, self.Role.SUPERVISOR, self.Role.MANAGER
        ) or self.is_superuser
 
    @property
    def is_viewer(self):
        return self.role in (
            self.Role.ADMIN, self.Role.SUPERVISOR,
            self.Role.MANAGER, self.Role.VIEWER,
        ) or self.is_superuser
 
    @property
    def is_reader(self):
        """All roles can read — reader is the minimum."""
        return True
 
    # --- Permission helpers -----------------------------------------------
 
    @property
    def can_manage_users(self):
        """Only admin can create/update/delete users."""
        return self.is_admin
 
    @property
    def can_delete_operations(self):
        """Admin and Supervisor can delete sell/return/write-off/invoices."""
        return self.is_supervisor
 
    @property
    def can_export(self):
        """Admin, Supervisor, Manager, Viewer can export."""
        return self.is_viewer
 
    @property
    def can_view_expenses(self):
        """Reader cannot see expenses."""
        return self.is_viewer
 
    @property
    def can_view_audit_log(self):
        """Only Admin and Supervisor see the audit log."""
        return self.is_supervisor
 
    @property
    def can_view_ttb(self):
        """Reader has no access to TTB report."""
        return self.is_viewer
 
    @property
    def can_export_ttb(self):
        """Manager and Reader cannot export TTB."""
        return self.is_supervisor
 
    @property
    def can_write(self):
        """Can create or update records."""
        return self.is_manager
 
    @property
    def can_delete_reference_data(self):
        """Delete batches, products, barcodes, etc."""
        return self.is_supervisor