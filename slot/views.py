from django.shortcuts import render,redirect
from .models import Freelancer,Client,Request,Slot
from .forms import ClientForm,FreelancerForm
from django.db.models import Q,Func
from django.db.models.expressions import RawSQL
from geocoder.distance import Distance
import math,geocoder,datetime
from django.contrib import messages
from django.urls import reverse

# Create your views here.


class Near(RawSQL):
    def __init__(self,latpoint, longpoint, *args,**kwargs):
        from django.db import connection
        connection.cursor()
        connection.connection.create_function('acos', 1, math.acos)
        connection.connection.create_function('cos', 1, math.cos)
        connection.connection.create_function('radians', 1, math.radians)
        connection.connection.create_function('sin', 1, math.sin)
        connection.connection.create_function('degrees', 1, math.degrees)
        query = "SELECT latitude, longitude, 111.045 * DEGREES(ACOS(COS(RADIANS(%s)) * COS(RADIANS(latitude)) * COS(RADIANS(%s) - RADIANS(longitude)) + SIN(RADIANS(%s)) * SIN(RADIANS(latitude)))) AS distance FROM slot_freelancer"
        super(Near, self).__init__(query,(latpoint, longpoint, latpoint), *args,**kwargs)

class NearBy(Func):
    function='distance'
    template = "%(function)s(%(expressions)s,'%(substring)s')"
    def __init__(self, expression, substring):
        
        super(NearBy, self).__init__(expression, substring=substring)
    def as_sqlite(self, compiler, connection):
        connection.cursor()
        connection.connection.create_function('distance', 2, Distance)
        return self.as_sql(compiler, connection, template=self.template)

#print(Freelancer.objects.annotate(dist=Near(latpoint=22.6857561,longpoint=88.33607649999999)))

def scoreUpdate(slot):
    freelancer = slot.request.freelancer
    score = {'5': 50, '15': 40, '30': 25, '60': 10, '90': 0}
    for key,value in score.items():
        if (slot.request.client.date-datetime.date.today()).days<=int(key):
            freelancer.credit_score-=value
            freelancer.save()
            break

def sendRequest(request):
    if request.POST:
        form=ClientForm(request.POST)
        if form.is_valid():
            client=form.save()
            # latlng = geocoder.google(client.venue).latlng
            # client.latitude = latlng[0]
            # client.longitude = latlng[1]
            # client.save()
            unavailabe_freelancer=Slot.objects.filter(request__client__date=client.date,status='00').values_list('request__freelancer',flat=True)
            availabe_freelancer=Freelancer.objects.exclude(pk__in=unavailabe_freelancer).annotate(distance=NearBy('venue',client.venue)).order_by('distance','-credit_score')
            if availabe_freelancer:
                Request.objects.create(freelancer=availabe_freelancer[0],client=client)
                client.status='01'  #01 for placed
                client.save()
                messages.success(request,'request confirmed')
            else:
                messages.info(request, 'No freelancer availabe now')
            return redirect('slot:client')
    else:
        form=ClientForm()
    return render(request,'slot/send.html',{'form':form})

def aceeptRequest(request,req_id):
    req=Request.objects.filter(id=req_id,client__status='01').first()   #01 for placed
    if req:
        req.status='01'     #01 FOR APPROVED 
        req.save()
        Slot.objects.create(request=req)
    else:
        messages.info(request,'already canceled')
    return redirect(reverse('slot:getrequest', kwargs={'freelancer': req.freelancer.id}))

def rejectRequest(request,req_id):
    req = Request.objects.filter(Q(client__status='00')|Q(client__status='01'),id=req_id).first() #00 Waiting and 01 placed
    if req:
        req.status='10' #10 for reject
        req.save()

        slot=Slot.objects.filter(request=req)
        if slot:    #when freelancer is approved request and then reject then this will be call
            slot.update(status='01')    #01 for REJECT
            scoreUpdate(slot.first())   # score update done here

        requested_freelancer=Request.objects.filter(client=req.client).values_list('freelancer')    #already requested freelancer
        unavailabe_freelancer=Slot.objects.filter(request__client__date=req.client.date,status='00').values_list('request__freelancer',flat=True)   #00 for approved    commited freelancer for that day
        availabe_freelancer=Freelancer.objects.exclude(Q(pk__in=unavailabe_freelancer)|Q(pk__in=requested_freelancer)).annotate(distance=NearBy('venue',req.client.venue)).order_by('distance','-credit_score')
        if availabe_freelancer:
            Request.objects.create(freelancer=availabe_freelancer[0], client=req.client)
            messages.success(request, 'request confirmed')
        else:
            req.client.status='00'  #00 waiting for placed
            req.client.save()
            messages.info(request, 'No freelancer availabe now')
    else:
        messages.info(request,'already canceled')
    return render(request,'slot/reject.html')

def cancelRequest(request,client_id):
    Client.objects.filter(id=client_id).update(status='10') #10 for CANCELED
    return redirect('slot:client')

def allFreelancer(request):
    freelancers=Freelancer.objects.all()
    return render(request,'slot/index.html',{'freelancers':freelancers})

def getRequest(request,freelancer):
    requests=Request.objects.filter(freelancer_id=freelancer)
    return render(request,'slot/request.html',{'requests':requests})

def clientDashboard(request):
    clients=Client.objects.all()    
    return render(request,'slot/client.html',{'clients':clients})

def clientRequest(request,client_id):
    req=Request.objects.filter(client_id=client_id).last()
    return render(request,'slot/clientreq.html',{'request':req})
    


def createRequest(freelancer):
    clients = Client.objects.filter(status='00')
    clients_date = clients.values_list('date', flat=True).distinct()
    for client_date in clients_date:
        client=clients.filter(date=client_date).first()
        client.status = '01'
        client.save()
        Request.objects.create(freelancer=freelancer,client=client)
def addFreelancer(request):
    if request.POST:
        form=FreelancerForm(request.POST)
        if form.is_valid():
            freelancer=form.save()
            transaction.on_commit(lambda:createRequest(freelancer=freelancer))
            messages.success(request,'Successfully added')
        return redirect('slot:freelancer')
    else:
        form=FreelancerForm()
    return render(request,'slot/add.html',{'form':form})


def complete(request,req_id):
    req=Request.objects.get(id=req_id)
    req.client.status='11'
    req.client.save()
    req.slot.status='11'
    req.slot.save()
    return redirect(reverse('slot:getrequest',kwargs={'freelancer':req.freelancer.id}))