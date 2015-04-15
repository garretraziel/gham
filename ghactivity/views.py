from django.shortcuts import render_to_response
from django.views.generic import DetailView
from django.template.context_processors import csrf
from django.shortcuts import redirect
from django.http import Http404
from django.conf import settings

from datetime import date
import github
from ghaminer import ghaminer as gm
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import Imputer
from sklearn.ensemble import GradientBoostingRegressor
import pandas as pd
from StringIO import StringIO

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

        values = []
        now = date.today()

        commits, time_created, time_ended = gm.get_all_commits(gh, owner, name)
        values.extend(gm.get_commits_stats(commits, time_created, now))

        issues, pulls = gm.get_all_issues_pulls(gh, owner, name)
        values.extend(gm.get_issues_stats(issues, time_created, now))
        values.extend(gm.get_issues_stats(pulls, time_created, now))

        events = gm.get_all_events(gh, owner, name)
        values.extend(gm.get_events_stats(events, time_created, now))

        values.extend(gm.get_contributors_stats(commits, time_created, now))

        ccomments = gm.get_all_commit_comments(gh, owner, name)
        values.extend(gm.get_commit_comments_stats(ccomments, time_created, now))

        forks = gm.get_all_forks(gh, owner, name)
        values.extend(gm.get_forks_stats(forks, time_created, now))

        duration = (now - time_created).days + 1
        values.append(str(duration))
        values.append(str(fork))

        prediction_string = ",".join(values)
        r = Repository(repository_id=rid, owner=owner, name=name, fork=str(fork),
                       first_commit=time_created, last_commit=time_ended, prediction_string=prediction_string)
        r.save()

        issues = [issue for issue, _ in issues]
        pulls = [pull for pull, _ in pulls]

        commits.sort(key=gm.get_commit_date)
        issues.sort(key=gm.get_direct_date)
        pulls.sort(key=gm.get_direct_date)
        forks.sort(key=gm.get_direct_date)

        if len(commits) != 0:
            t_date = gm.get_commit_date(commits[0])
            count = 0
            for commit in commits:
                if gm.get_commit_date(commit) == t_date:
                    count += 1
                else:
                    CommitCount.objects.create(count=count, date=t_date, repository=r)
                    t_date = gm.get_commit_date(commit)
                    count = 1
            CommitCount.objects.create(count=count, date=t_date, repository=r)

        return redirect("repo_detail", pk=rid)


class RepositoryDetail(DetailView):
    model = Repository

    @classmethod
    def load_clf(cls, filename):
        csv = pd.read_csv(filename, na_values=["nan"])
        X_csv = csv.iloc[:, :-1].copy()
        y_csv = csv['result'].copy()

        cls.v = DictVectorizer(sparse=False)
        cls.i = Imputer()
        cls.clf = GradientBoostingRegressor()
        X = cls.v.fit_transform(X_csv.transpose().to_dict().values())
        X = cls.i.fit_transform(X)
        y = y_csv.as_matrix()
        cls.clf.fit(X, y)

    def get_context_data(self, **kwargs):
        context = super(RepositoryDetail, self).get_context_data(**kwargs)
        pred_str = context['repository'].prediction_string
        f = StringIO(pred_str)
        csv = pd.read_csv(f, names=gm.ATTRS, header=None, na_values=["nan"])
        X = self.v.transform(csv.transpose().to_dict().values())
        X = self.i.transform(X)
        context['prediction'] = self.clf.predict(X)
        return context