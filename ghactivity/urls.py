from django.conf.urls import url
from .views import get_repo_info, RepositoryDetail
import os

this_dir = os.path.dirname(os.path.realpath(__file__))
RepositoryDetail.load_clf(os.path.join(this_dir, "datasets/fin_percentage.csv"))

urlpatterns = [
    url(r'^$', get_repo_info, name="get_repo_info"),
    url(r'^(?P<pk>\d+)$', RepositoryDetail.as_view(), name="repo_detail"),
]
