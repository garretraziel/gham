from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<owner>[A-Za-z0-9_.-]+)/(?P<name>[A-Za-z0-9_.-]+)$', views.get_repo_info, name="get_repo_info"),
]
