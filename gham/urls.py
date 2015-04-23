from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from .views import index, logout_user

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^logout/$', logout_user, name='logout'),
    url(r'^model/$', TemplateView.as_view(template_name="model.html"), name='model'),
    url(r'^dataset/$', TemplateView.as_view(template_name="dataset.html"), name='dataset'),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name='about'),

    url(r'^activity/', include('ghactivity.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
]
