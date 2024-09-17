import uuid
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from common.kgs import generate_unique_id
from user.enums import RoleEnum, BulkStatusEnum, TOKEN_TYPE
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager, EligibleUserUploadManager, TokenManager
from common.models import AuditableModel
from django.core.validators import MinValueValidator


class Department(AuditableModel):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    code = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return str(self.id)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(max_length=50, primary_key=True, default=generate_unique_id, editable=False)
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    password = models.CharField(max_length=600, null=True)
    firstname = models.CharField(max_length=255, null=True, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=17, blank=True, null=True)
    image = models.FileField(upload_to='user_images/', blank=True, null=True)
    role = models.CharField(max_length=100, choices=RoleEnum.choices())
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    matric_no = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.email

    def save_last_login(self):
        self.last_login = datetime.now()
        self.save()


class Token(models.Model):
    objects = TokenManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.CharField(max_length=255, null=True)
    token_type = models.CharField(
        max_length=100, choices=TOKEN_TYPE, default='LoginToken')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EligibleUserUpload(AuditableModel):
    objects = EligibleUserUploadManager()
    file = models.FileField(upload_to='users/bulk')
    number_of_valid = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    number_of_invalid = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    total_upload = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    error_file = models.FileField(upload_to='users/bulk', null=True, blank=True)
    created_by = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=100, choices=BulkStatusEnum.choices(), default=BulkStatusEnum.Started.value)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return str(self.id)



