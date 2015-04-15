from django.conf.urls import url
from django.conf import settings
from .views import get_repo_info, RepositoryDetail, RepositoryListView

RepositoryDetail.load_clf(settings.DATASET_NAME)

urlpatterns = [
    url(r'^$', get_repo_info, name="get_repo_info"),
    url(r'list/$', RepositoryListView.as_view(), name="repo_list"),
    url(r'^(?P<pk>\d+)$', RepositoryDetail.as_view(), name="repo_detail"),
]
