from django.conf.urls import url
from django.conf import settings
from .views import get_repo_info, status_json, RepositoryDetail, RepositoryListView, get_repo_commits, get_repo_forks, \
    get_repo_issues, get_repo_pulls, DeleteRepositoryView, update_repository, get_repo_badge

# This is used for learning/loading prediction model at the beginning
RepositoryDetail.load_clf(settings.DATASET_NAME)

urlpatterns = [
    url(r'^$', RepositoryListView.as_view(), name="repo_list"),
    url(r'^get/$', get_repo_info, name="get_repo_info"),
    url(r'^status/$', status_json),
    url(r'^(?P<pk>\d+)$', RepositoryDetail.as_view(), name="repo_detail"),
    url(r'^(?P<pk>\d+)/commits$', get_repo_commits),
    url(r'^(?P<pk>\d+)/issues$', get_repo_issues),
    url(r'^(?P<pk>\d+)/pulls$', get_repo_pulls),
    url(r'^(?P<pk>\d+)/forks$', get_repo_forks),
    url(r'^(?P<pk>\d+)/update$', update_repository, name="repo_update"),
    url(r'^(?P<pk>\d+)/delete$', DeleteRepositoryView.as_view(), name="repo_delete"),
    url(r'^(?P<pk>\d+)/badge\.svg$', get_repo_badge, name="repo_badge")
]
