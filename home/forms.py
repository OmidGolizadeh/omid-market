from django import forms
from .models import Contact_us


class Contact_Form(forms.ModelForm):
    class Meta:
        model = Contact_us
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'name': 'name',
                'id': 'name',
                'placeholder': 'نام خود وارد کنید',
                'required': '',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'name': 'tel',
                'id': 'tel',
                'placeholder': 'شماره تلفن خود وارد کنید',
                'required': '',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'name': 'email',
                'id': 'email',
                'placeholder': 'ایمیل خود وارد کنید ',
                'style': 'text-align: right; direction: rtl;',
                'required': '',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'name': 'subject',
                'id': 'subject',
                'placeholder': 'موضوع خود وارد کنید',
                'required': '',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'name': 'message',
                'id': 'message',
                'placeholder': 'پیام خود را وارد کنید',
                'required': '',
                'rows': '3'
            })
        }
