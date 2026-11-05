from django.db import models
from django_jalali.db import models as jmodels
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
    phone_number = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name='شماره تلفن')
    image = models.ImageField(upload_to='images/users', null=True, blank=True, verbose_name='تصویر')
    date_of_birth = jmodels.jDateField(null=True, blank=True, verbose_name='تاریخ تولد ')
    landline = models.CharField(max_length=11, null=True, blank=True, verbose_name='تلفن ثابث')
    card_number = models.CharField(max_length=16, unique=True, null=True, blank=True, verbose_name='شماره کارت  ')
    national_code = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name='کد ملی ')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_admin = models.BooleanField(default=False, verbose_name='ادمین')
    created_at = jmodels.jDateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='تاریخ ایجاد احساب')

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


class Otp(models.Model):
    token = models.CharField(max_length=200, null=True, verbose_name='توکن')
    username = models.CharField(max_length=255, verbose_name='نام کاربری')
    email = models.EmailField(max_length=255, null=True, verbose_name='ایمیل')
    phone_number = models.CharField(max_length=11, null=True, blank=True, verbose_name='شماره تلفن')
    code = models.SmallIntegerField(verbose_name='کد', db_index=True)
    password = models.CharField(max_length=255, null=True, verbose_name='رمز')
    expiration_date = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    class Meta:
        verbose_name = 'کد یک بار مصرف'
        verbose_name_plural = 'کد ها یک بار مصرف'

    def __str__(self):
        return self.username


class Province(models.Model):
    name = models.CharField(max_length=60, verbose_name='استان')

    class Meta:
        verbose_name = 'استان'
        verbose_name_plural = 'استان ها'

    def __str__(self):
        return self.name


class City(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities', verbose_name='استان')
    name = models.CharField(max_length=60, verbose_name='شهر')

    class Meta:
        verbose_name = 'شهر'
        verbose_name_plural = 'شهر ها'
        unique_together = ('name', 'province')

    def __str__(self):
        return f'{self.province}-{self.name}'


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address', verbose_name='کاربر')
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='address', verbose_name='استان')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='address', verbose_name='شهر')
    full_address = models.CharField(max_length=255, verbose_name='آدرس')
    postal_code = models.CharField(max_length=10, verbose_name='کد پستی')
    receiver_delivery = models.CharField(max_length=255, verbose_name='تحویل گیرنده')
    mobile_phone_number = models.CharField(max_length=11, verbose_name='شماره تلفن همراه')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ')

    def __str__(self):
        return f'{self.user}-{self.province}-{self.city}-{self.postal_code}'

    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس ها'
