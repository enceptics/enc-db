from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import EmailValidator

from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', self.model.SUPERUSER)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):  # 🔹 Ensure this is implemented
        return self.get(email=email)

class User(AbstractBaseUser, PermissionsMixin):
    SUPERUSER = 'superuser'
    CUSTOMER = 'customer'
    PROPERTY_MANAGER = 'property_manager'
    MANAGER = 'manager'
    SUB_MANAGER = 'sub_manager'

    ROLE_CHOICES = [
        (SUPERUSER, 'Superuser'),
        (CUSTOMER, 'Customer'),
        (PROPERTY_MANAGER, 'Property Manager'),
        (MANAGER, 'Manager'),
        (SUB_MANAGER, 'Sub-Manager'),
    ]
    
    username = None  
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default=CUSTOMER)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    email = models.EmailField(unique=True, validators=[EmailValidator()], blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    date_joined = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)  # ✅ Important for login
    is_staff = models.BooleanField(default=False)  # ✅ Required for admin access
    is_superuser = models.BooleanField(default=False)  # ✅ Required for superusers

    # Override related names to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()  # Ensure the manager is explicitly set

    # Set email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.get_role_display()})'

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    current_city = models.CharField(max_length=50, blank=True, null=True, default=None)
    profile_pic = models.ImageField(
        upload_to='profile_pics',
        default='default.png',
        blank=True,
        null=False,
    )
    bio = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email

