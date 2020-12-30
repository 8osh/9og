from django import forms
from .models import Post, Category, Comment
from captcha.fields import ReCaptchaField
import datetime

choises = Category.objects.all().values_list('name', 'name')
choise_list = []

for item in choises:
    choise_list.append(item)


class PostForm(forms.ModelForm):
    #captcha = ReCaptchaField()
    class Meta:
        model = Post
        fields = [
            'title',
            'category',
            'content',
            'thumbnail',
            'created_on',
            'edited_on',
            'status',
            'tags',
        ]
        widgets = {
            'category'  : forms.Select(choices=choise_list),
            'created_on': forms.TextInput(attrs={}),
            'thumbnail' : forms.FileInput(attrs={
                'class'  : 'custom-file-upload',
            }),
        }

class CommentForm(forms.ModelForm):
    captcha = ReCaptchaField()
    class Meta:
        model   = Comment
        fields  = [
            'name',
            'email',
            'content',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder':'İsminiz'}),
            'email': forms.TextInput(attrs={'placeholder':'Mail adresiniz'}),
            'content': forms.Textarea(attrs={
                'placeholder'   :'Yorumunuz',
                'class'         : 'message',
                'cols'          :10,
                'rows'          :10,
                }),
        }

def should_be_empty(value):
    if value:
        raise forms.ValidationError('Input boş değil!')

