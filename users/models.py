import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin

# Create your models here.
class UserManager(UserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError("User must have email adress")

        if not password:
            raise ValueError("User must have password")

        user = self.model(
            email = self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password):
        if not email:
            raise ValueError("User must have email adress")

        if not password:
            raise ValueError("User must have password")

        user = self.create_user(
            email = self.normalize_email(email),
            password = password
        )
        user.is_admin=True
        user.is_superadmin=True
        user.is_active=True
        user.is_staff=True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=50, default="")

    # required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    objects =  UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True