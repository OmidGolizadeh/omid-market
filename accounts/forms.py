from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.core.exceptions import ValidationError
from accounts.models import User, Address, Province, City
from django.core import validators


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='رمز', widget=forms.PasswordInput)
    password2 = forms.CharField(label='تکرار زمز', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'full_name', 'phone_number', 'landline', 'image', 'date_of_birth',
                  'national_code', 'card_number']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('رمزهای عبور مطابقت ندارند')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label='رمز عبور')

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'phone_number', 'landline', 'image', 'date_of_birth',
                  'national_code', 'card_number']


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control', 'name': 'username', 'id': 'username', 'placeholder': 'نام کاربری'
    }))
    password = forms.CharField(max_length=255, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'name': 'password', 'id': 'password', 'placeholder': 'رمز عبور'
    }))


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control', 'name': 'username', 'id': 'username', 'placeholder': 'نام کاربری'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'name': 'email', 'id': 'email', 'placeholder': 'ایمیل',
        'style': 'text-align: right; direction: rtl;',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'name': 'password1', 'id': 'password1', 'placeholder': 'رمز عبور '
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'name': 'password2', 'id': 'password2', 'placeholder': 'تکرار رمز عبور '
    }))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('این نام کاربری قبلاً ثبت شده است.', code='username_taken')

        if username and len(username) < 4:
            raise ValidationError('نام کاربری باید حداقل 4 کاراکتر باشد.', code='username_too_short')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('این ایمیل قبلاً ثبت شده است.', code='email_taken')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError('رمزهای عبور یکسان نیستند.', code='password_taken')
            if len(password1) < 4:
                raise ValidationError('رمز عبور باید حداقل ۴ کاراکتر باشد.', code='password_len_taken')

        return cleaned_data


class CheckOtpForm(forms.Form):
    code = forms.CharField(max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control', 'name': 'code', 'id': 'code', 'placeholder': 'کد'
    }), validators=[validators.MaxLengthValidator(4)])


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['province', 'city', 'full_address', 'postal_code', 'receiver_delivery', 'mobile_phone_number']
        widgets = {
            'province': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_province',

            }),
            'city': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_city',

            }),
            'full_address': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'address',
                'placeholder': 'آدرس کامل را وارد کنید'

            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'postal_code',
                'placeholder': 'کد پستی ۱۰ رقمی',

            }),
            'receiver_delivery': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'receiver',
                'placeholder': 'نام تحویل‌گیرنده'

            }),
            'mobile_phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'tel',
                'placeholder': '۰۹XXxxxxxxx'

            })
        }
        labels = {
            'province': 'استان',
            'city': 'شهر',
            'full_address': 'آدرس کامل',
            'postal_code': 'کد پستی',
            'receiver_delivery': 'تحویل‌گیرنده',
            'mobile_phone_number': 'شماره موبایل',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['province'].queryset = Province.objects.all().order_by('name')
        self.fields['province'].empty_label = 'استان را انتخاب کنید'

        self.fields['city'].queryset = City.objects.none()
        self.fields['city'].empty_label = 'ابتدا استان را انتخاب کنید'

        if 'province' in self.data:
            try:
                province_id = int(self.data.get('province'))
                self.fields['city'].queryset = City.objects.filter(
                    province_id=province_id
                ).order_by('name')
            except (ValueError,TypeError):
                pass
        elif self.instance.pk and self.instance.province_id:
            self.fields['city'].queryset = City.objects.filter(
                province=self.instance.province
            ).order_by('name')

