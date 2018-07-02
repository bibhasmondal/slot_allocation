from django.db import models
from django.core.validators import RegexValidator
# Create your models here.

class Freelancer(models.Model):
    username = models.CharField(max_length=50, unique=True)
    name=models.CharField(max_length=50)
    credit_score = models.IntegerField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{10,13}$', message="Phone number must be entered in the format: '+999999999'. Up to 13 digits allowed.")
    ph_no=models.CharField(max_length=13, validators=[phone_regex], blank=True)
    def __str__(self):
        return self.name


class Client(models.Model):
    STAT_CHOICES=(('00','CONFIRMED'),('01','CANCELED'),('10','COMPLETED'))
    name = models.CharField(max_length=50)
    datetime = models.DateTimeField()
    venue = models.CharField(max_length=50)
    status = models.CharField(choices=STAT_CHOICES, max_length=2,default='00')
    def __str__(self):
        return '%s--%s--%s'%(self.name,self.datetime,self.status)

class Request(models.Model):
    STAT_CHOICES = (('00', 'WAITING'),('01', 'APPROVED'), ('10', 'REJECTED'))
    freelancer = models.ForeignKey(Freelancer,on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    status = models.CharField(choices=STAT_CHOICES, max_length=2,default='00')
    def __str__(self):
        return '%s--%s--%s' % (self.client, self.freelancer,self.status)

class Slot(models.Model):
    STAT_CHOICES = (('00', 'APPROVED'), ('01', 'REJECTED'),('10', 'CANCELED'),('11', 'COMPLETED'))
    request=models.OneToOneField(Request,on_delete=models.CASCADE,limit_choices_to={'status':'01'})
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    status = models.CharField(choices=STAT_CHOICES, max_length=2,default='00')

    def __str__(self):
        return '%s--%s' % (self.request, self.status)
 
