from django.shortcuts import render
from .models import *
import random
from django.http import HttpResponse
from django.shortcuts import render
from .forms import ClientForm
from django.db.models import Q
# Create your views here.

def sendRequest(request):
    if request.POST:
        form=ClientForm(request.POST)
        if form.is_valid():
            client=form.save()
            unavailabe_freelancer=Slot.objects.filter(request__client__datetime=client.datetime,status='00').values_list('request__freelancer',flat=True)
            availabe_freelancer=Freelancer.objects.exclude(pk__in=unavailabe_freelancer)
            allocate_freelancer=random.choice(availabe_freelancer)
            Request.objects.create(freelancer=allocate_freelancer,client=client)
    else:
        form=ClientForm()
    return render(request,'slot/send.html',{'form':form})

def aceeptRequest(request,req_id):
    req=Request.objects.filter(id=req_id).first()
    req.status='01'     #01 FOR APPROVED
    req.save()
    Slot.objects.create(request=req)
    return HttpResponse('Complete')

def rejectRequest(request,req_id):
    req = Request.objects.filter(id=req_id,client__status='00').first() #00 CONFIRMED
    if req:
        req.status='10'
        req.save()
        slot=Slot.objects.filter(request=req)
        if slot:
            slot.update(status='01')    #01 for REJECT
        requested_freelancer=Request.objects.filter(client=req.client).values_list('freelancer')    
        unavailabe_freelancer=Slot.objects.filter(request__client__datetime=req.client.datetime,status='00').values_list('request__freelancer',flat=True)   #00 for approved
        availabe_freelancer=Freelancer.objects.exclude(Q(pk__in=unavailabe_freelancer)|Q(pk__in=requested_freelancer))
        if availabe_freelancer:
            reallocate_freelancer = random.choice(availabe_freelancer)
            Request.objects.create(freelancer=reallocate_freelancer, client=req.ClientForm) 
    return render(request,'slot/reject.html')

def cancelRequest(request):
    Client.objects.filter(id=request.GET['client']).update(status='01') #01 for CANCELED
    return HttpResponse('Successfull')

def allFreelancer(request):
    freelancers=Freelancer.objects.all()
    return render(request,'slot/index.html',{'freelancers':freelancers})

def getRequest(request,freelancer):
    requests=Request.objects.filter(freelancer_id=freelancer,status='00',client__status='00')   #00 for waiting request and 00 for confirmed client
    return render(request,'slot/request.html',{'requests':requests})
