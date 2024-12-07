from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    def create_user(self, email, userName, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, userName=userName, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, userName, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, userName, password, **extra_fields)

class Login(AbstractBaseUser):


    id = models.AutoField(primary_key=True)
    userName = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    phoneNum = models.CharField(max_length=15, null=True, blank=True)
    company = models.ForeignKey('company.CompanyDetails', null=True, blank=True, on_delete=models.SET_NULL, related_name='companydetails')
    role = models.CharField(max_length=20)
    is_company_setup_complete = models.BooleanField(default=False)
    is_payroll_setup_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['userName']

    def __str__(self):
        return self.userName

    def save(self, *args, **kwargs):
        # Hash the password before saving
        if self.password and not self.password.startswith('pbkdf2_sha256'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
