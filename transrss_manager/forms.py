from django import forms

class FeedAddForm(forms.Form):
    title = forms.CharField(label='title', max_length=255)
    url = forms.CharField(label='url', max_length=255)

class MatcherAddForm(forms.Form):
    pattern = forms.CharField(label='pattern', max_length=255)
    download_dir = forms.CharField(label='download_dir', max_length=255)
