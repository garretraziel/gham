from django.conf.urls import url
from .views import get_repo_info, RepositoryDetail

urlpatterns = [
    url(r'^$', get_repo_info, name="get_repo_info"),
    url(r'^(?P<pk>\d+)$', RepositoryDetail.as_view(), name="repo_detail"),
]
