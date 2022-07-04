from django import forms

class FeedAddForm(forms.Form):
    title = forms.CharField(label='title', max_length='255')
    url = forms.CharField(label='url', max_length='255')