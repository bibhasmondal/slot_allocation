from django import forms
from .models import Client,Freelancer
class ClientForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateTimeInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.DateTimeInput(attrs={'type': 'time'}))
    class Meta:
        model=Client
        fields=['name','date','time','venue']

class FreelancerForm(forms.ModelForm):
    class Meta:
        model=Freelancer
        fields=['username','name','ph_no','venue']