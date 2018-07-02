from django import forms
from .models import Client
class ClientForm(forms.ModelForm):
    datetime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'date', 'class': 'form-control'}))
    class Meta:
        model=Client
        fields=['name','datetime','venue']
