from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'gham.views.home', name='home'),
    url(r'^activity/', include('ghactivity.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
