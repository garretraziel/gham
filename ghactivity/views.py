from django.shortcuts import render_to_response
from django.views.generic import DetailView
from django.template.context_processors import csrf
from django.shortcuts import redirect
from django.http import Http404
from django.conf import settings

import github
from ghaminer import ghaminer as gm

from .models import Repository, CommitCount


def get_repo_info(request):
    if request.method == 'GET':
        c = {}
        c.update(csrf(request))
        return render_to_response("ghactivity/index.html", c)
    elif request.method == 'POST':
        full_name = request.POST['repository']
        owner, name = full_name.split("/", 1)

        if Repository.objects.filter(owner=owner).filter(name=name).count() != 0:
            r = Repository.objects.filter(owner=owner).filter(name=name).get()
            return redirect("repo_detail", pk=r.pk)

        gh = github.GitHub(username=settings.GITHUB_USERNAME,
                           password=settings.GITHUB_PASSWORD)
        try:
            rid, full_name, fork, created_at = gm.get_basic_repo_info(gh, owner, name)
        except github.ApiNotFoundError:
            raise Http404("No such repo exists.")

        commits, first_commit, last_commit = gm.get_all_commits(gh, owner, name)
        issues, pulls = gm.get_all_issues_pulls(gh, owner, name)
        forks = gm.get_all_forks(gh, owner, name)
        issues = [issue for issue, _ in issues]
        pulls = [pull for pull, _ in pulls]

        commits.sort(key=gm.get_commit_date)
        issues.sort(key=gm.get_direct_date)
        pulls.sort(key=gm.get_direct_date)
        forks.sort(key=gm.get_direct_date)

        r = Repository(repository_id=rid, owner=owner, name=name, fork=str(fork),
                       first_commit=first_commit, last_commit=last_commit)
        r.save()

        if len(commits) != 0:
            date = gm.get_commit_date(commits[0])
            count = 0
            for commit in commits:
                if gm.get_commit_date(commit) == date:
                    count += 1
                else:
                    CommitCount.objects.create(count=count, date=date, repository=r)
                    date = gm.get_commit_date(commit)
                    count = 1
            CommitCount.objects.create(count=count, date=date, repository=r)

        return redirect("repo_detail", pk=rid)


class RepositoryDetail(DetailView):
    model = Repository
