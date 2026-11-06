from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body', 'parent']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control','id':'body', 'rows': '4', 'placeholder': 'متن کامنت', }),
            'parent': forms.HiddenInput(attrs={'class': 'form-control', 'id': 'id_parent'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].required = False
        self.fields['parent'].required = False
        self.fields['body'].widget.attrs['id'] = 'body'
