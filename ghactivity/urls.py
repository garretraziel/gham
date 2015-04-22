from django.conf.urls import url
from django.conf import settings
from .views import get_repo_info, status_json, RepositoryDetail, RepositoryListView, get_repo_commits, get_repo_forks, \
    get_repo_issues, get_repo_pulls, DeleteRepositoryView, update_repository

RepositoryDetail.load_clf(settings.DATASET_NAME)

urlpatterns = [
    url(r'^get/$', get_repo_info, name="get_repo_info"),
    url(r'list/$', RepositoryListView.as_view(), name="repo_list"),
    url(r'status/$', status_json),
    url(r'^(?P<pk>\d+)$', RepositoryDetail.as_view(), name="repo_detail"),
    url(r'^(?P<pk>\d+)/commits$', get_repo_commits),
    url(r'^(?P<pk>\d+)/issues', get_repo_issues),
    url(r'^(?P<pk>\d+)/pulls', get_repo_pulls),
    url(r'^(?P<pk>\d+)/forks', get_repo_forks),
    url(r'^(?P<pk>\d+)/update', update_repository, name="repo_update"),
    url(r'^(?P<pk>\d+)/delete', DeleteRepositoryView.as_view(), name="repo_delete")
]
