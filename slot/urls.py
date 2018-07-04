from django.conf.urls import url
from .views import *
app_name='slot'
urlpatterns = [
    url(r'^$',sendRequest),
    url(r'^accept/(?P<req_id>[0-9]+)/$', aceeptRequest, name="accept"),
    url(r'^reject/(?P<req_id>[0-9]+)/$', rejectRequest, name="reject"),
    url(r'^cancel/$', cancelRequest,name='cancel'),
    url(r'^freelancer/$', allFreelancer,name='freelancer'),
    url(r'^add/$', addFreelancer, name='add'),
    url(r'^client/$', clientDashboard,name='client'),
    url(r'^freelancer/(?P<freelancer>[0-9]+)/$', getRequest,name='getrequest'),
    url(r'^client/(?P<client_id>[0-9]+)/$', clientRequest,name='clientrequest'),
]
