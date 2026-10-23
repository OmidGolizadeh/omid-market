from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body', 'parent']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'name': 'body',
                'id': 'body',
                'rows': '4',
                'required': True,
                'oninvalid': "this.setCustomValidity('لطفاً متن دیدگاه خود را وارد کنید.')",
                'oninput': "this.setCustomValidity('')"
            }),
            'parent': forms.HiddenInput(attrs={
                'class': 'form-control',
                'name': 'parent_id',
                'id': 'parent_id',
                'value': ''
            })
        }
