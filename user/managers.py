from django.contrib.auth.base_user import BaseUserManager
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where username is the unique identifiers
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('verified', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        user = self.create_user(email, password, **extra_fields)
        user.role = 'SuperAdmin'
        user.save()
        return user

    def active(self) -> QuerySet:
        queryset = self.get_queryset()
        return queryset.filter(is_active=True, verified=True)

    def get_by_natural_key(self, username):
        case_insensitive_username_field = "{}__iexact".format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class TokenManager(models.Manager):
    pass


class EligibleUserUploadManager(models.Manager):
    pass
