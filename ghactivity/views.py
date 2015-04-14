from django.shortcuts import render_to_response
from django.views.generic import DetailView
from django.template.context_processors import csrf
from django.shortcuts import redirect
from django.http import Http404

import github
from ghaminer import ghaminer as gm
from datetime import date, datetime

from .models import Repository


def get_repo_info(request):
    if request.method == 'GET':
        c = {}
        c.update(csrf(request))
        return render_to_response("ghactivity/index.html", c)
    elif request.method == 'POST':
        try:
            full_name = request.POST['repository']
            owner, name = full_name.split("/", 1)

            if Repository.objects.filter(owner=owner).filter(name=name).count() != 0:
                r = Repository.objects.filter(owner=owner).filter(name=name).get()
                return redirect("repo_detail", pk=r.id)

            gh = github.GitHub()  # TODO: login
            today = date.today()
            now = datetime.now()

            commits, first_commit, last_commit = gm.get_all_commits(gh, owner, name)
            issues = gm.get_all_issues_pulls(gh, owner, name)
            forks = gm.get_all_forks(gh, owner, name)

            commits.sort(key=gm.get_commit_date)
            issues.sort(key=gm.get_direct_date)
            forks.sort(key=gm.get_direct_date)

            #return render_to_response("ghactivity/")
        except github.ApiNotFoundError:
            raise Http404("No such repo exists.")


class RepositoryDetail(DetailView):
    mode = Repository
