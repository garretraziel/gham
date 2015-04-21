from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy

from .views import index, logout_user

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^logout/$', logout_user, name='logout'),

    url(r'^activity/', include('ghactivity.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
]
