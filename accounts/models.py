from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("نام کاربری الزامی است")

        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(
            username=username,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, verbose_name='نام کاربری ')
    full_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام کامل')
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True, verbose_name='ایمیل')
    phone_number = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره تلفن')
    image = models.ImageField(upload_to='images/users', null=True, blank=True, verbose_name='تصویر')
    date_of_birth = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ تولد ')
    landline = models.CharField(max_length=11, null=True, blank=True, verbose_name='تلفن ثابث')
    card_number = models.CharField(max_length=16, unique=True, null=True, blank=True, verbose_name='شماره کارت  ')
    national_code = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name='کد ملی ')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_admin = models.BooleanField(default=False, verbose_name='ادمین')

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.username} - {self.full_name} '

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربر ها'

    @property
    def is_staff(self):
        return self.is_admin
