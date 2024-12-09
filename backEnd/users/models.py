from django.contrib.auth.models import AbstractUser
from django.db import models
from branches.models import Branch

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('branch_manager', 'Branch Manager'),
        ('employee', 'Employee'),
    ]

    # Add related_name to these fields
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

    birthday = models.DateField(null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return self.username