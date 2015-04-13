from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse

urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse('get_repo_info'))),
    url(r'^activity/', include('ghactivity.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
