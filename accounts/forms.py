from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.core.exceptions import ValidationError
from accounts.models import User


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
