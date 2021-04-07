from django import forms

from .models import Post, Comment


def clean_artist(value):
    if value == '':
        raise forms.ValidationError(
            'А кто поле будет заполнять, Пушкин?',
            params={'value': value})


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = 'text',
