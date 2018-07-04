from django import forms
from .models import Client,Freelancer
class ClientForm(forms.ModelForm):
    datetime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'date', 'class': 'form-control'}))
    class Meta:
        model=Client
        fields=['name','datetime','venue']

class FreelancerForm(forms.ModelForm):
    class Meta:
        model=Freelancer
        fields=['username','name','ph_no','venue']