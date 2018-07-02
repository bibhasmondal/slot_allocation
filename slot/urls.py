from django.conf.urls import url
from .views import *
app_name='slot'
urlpatterns = [
    url(r'^send/$',sendRequest),
    url(r'^accept/(?P<req_id>[0-9]+)/$', aceeptRequest, name="accept"),
    url(r'^reject/(?P<req_id>[0-9]+)/$', rejectRequest, name="reject"),
    url(r'^cancel/$', cancelRequest),
    url(r'^$', allFreelancer),
    url(r'^(?P<freelancer>[0-9]+)/$', getRequest,name='getrequest'),
]