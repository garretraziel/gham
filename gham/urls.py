from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy

urlpatterns = [
    url(r'^$', RedirectView.as_view(url=reverse_lazy('repo_list'), permanent=True)),
    url(r'^activity/', include('ghactivity.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
