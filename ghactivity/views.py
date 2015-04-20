from django.shortcuts import render_to_response
from django.views.generic import DetailView, ListView
from django.template.context_processors import csrf
from django.shortcuts import redirect
from django.http import Http404
from django.conf import settings
from django.http import JsonResponse

import github
from ghaminer import ghaminer as gm
import os
from sklearn.externals import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import Imputer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
import pandas as pd
from StringIO import StringIO
import threading
import datetime

from .models import Repository, Author, CommitCount, IssuesCount, ClosedIssuesCount, ClosedIssuesTime, PullsCount, \
    ClosedPullsCount, ClosedPullsTime, ForksCount


def create_count_series(values, get_date, obj, repository):
    if len(values) != 0:
        to_create = []
        t_date = get_date(values[0])
        count = 0
        for value in values:
            if get_date(value) == t_date:
                count += 1
            else:
                to_create.append(obj(count=count, date=t_date, repository=repository))
                t_date = get_date(value)
                count = 1
        to_create.append(obj(count=count, date=t_date, repository=repository))
        obj.objects.bulk_create(to_create)


def create_average_series(values, get_date, get_value, obj, repository):
    if len(values) != 0:
        to_create = []
        t_date = get_date(values[0])
        count = 0
        s = 0.0
        for value in values:
            if get_date(value) == t_date:
                count += 1
                s += get_value(value)
            else:
                avg = s / count
                to_create.append(obj(count=avg, date=t_date, repository=repository))
                t_date = get_date(value)
                count = 1
                s = 0.0
        avg = s / count
        to_create.append(obj(count=avg, date=t_date, repository=repository))
        obj.objects.bulk_create(to_create)


def download_repo_info(owner, name, repository):
    gh = github.GitHub(username=settings.GITHUB_USERNAME,
                       password=settings.GITHUB_PASSWORD)

    commits, issues, pulls, forks, time_created, time_ended, contributors, predict = gm.get_repo_stats(gh, owner, name,
                                                                                                       False)

    repository.first_commit = time_created
    repository.last_commit = time_ended
    repository.contributors = contributors
    repository.prediction_string = predict

    issues = [issue for issue, _ in issues]
    pulls = [pull for pull, _ in pulls]

    commits.sort(key=gm.get_commit_date)
    issues.sort(key=gm.get_direct_date)
    pulls.sort(key=gm.get_direct_date)
    forks.sort(key=gm.get_direct_date)

    create_count_series(commits, gm.get_commit_date, CommitCount, repository)
    create_count_series(issues, gm.get_direct_date, IssuesCount, repository)

    issues = [issue for issue in issues if issue['state'] == 'closed']
    issues.sort(key=gm.get_close_date)
    create_count_series(issues, gm.get_close_date, ClosedIssuesCount, repository)
    create_average_series(issues, gm.get_close_date, gm.get_time_to_close, ClosedIssuesTime, repository)

    create_count_series(pulls, gm.get_direct_date, PullsCount, repository)
    pulls = [pull for pull in pulls if pull['state'] == 'closed']
    pulls.sort(key=gm.get_close_date)
    create_count_series(pulls, gm.get_close_date, ClosedPullsCount, repository)
    create_average_series(pulls, gm.get_close_date, gm.get_time_to_close, ClosedPullsTime, repository)

    create_count_series(forks, gm.get_direct_date, ForksCount, repository)

    repository.fresh = True
    repository.save()


def get_repo_info(request):
    if request.method == 'GET':
        c = {}
        c.update(csrf(request))
        return render_to_response("ghactivity/repository_get.html", c)
    elif request.method == 'POST':
        full_name = request.POST['repository']
        owner, name = full_name.split("/", 1)

        author, _ = Author.objects.get_or_create(name=owner)

        existing = Repository.objects.filter(owner__pk=author.pk).filter(name=name)
        if existing.exists():
            r = existing.get()
            if r.fresh:
                return redirect("repo_detail", pk=r.pk)
            else:
                return redirect("repo_list")

        gh = github.GitHub(username=settings.GITHUB_USERNAME,
                           password=settings.GITHUB_PASSWORD)

        try:
            rid, full_name, fork, created_at = gm.get_basic_repo_info(gh, owner, name)
        except github.ApiNotFoundError:
            raise Http404("No such repo exists.")

        r = Repository(repository_id=rid, owner=author, name=name, fork=str(fork))
        r.save()

        t = threading.Thread(target=download_repo_info, args=(owner, name, r))
        t.start()

        return redirect("repo_list")


class RepositoryDetail(DetailView):
    queryset = Repository.objects.filter(fresh=True)

    @classmethod
    def load_clf(cls, datasetname):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(this_dir, "datasets/%s" % datasetname)
        modelname = os.path.join(this_dir, "models/%s.pkl" % datasetname)
        if os.path.exists(modelname):
            cls.pipeline = joblib.load(modelname)
            return

        csv = pd.read_csv(filename, na_values=["nan", "?"])
        x_csv = csv.iloc[:, :-1].copy()
        y_csv = csv['result'].copy()
        x = x_csv.transpose().to_dict().values()
        y = y_csv.as_matrix()

        v = DictVectorizer(sparse=False)
        i = Imputer()
        clf = GradientBoostingRegressor()
        cls.pipeline = Pipeline([('vectorizer', v), ('imputer', i), ('regressor', clf)])
        cls.pipeline.fit(x, y)
        joblib.dump(cls.pipeline, modelname)

    def get_context_data(self, **kwargs):
        context = super(RepositoryDetail, self).get_context_data(**kwargs)
        pred_str = context['repository'].prediction_string
        f = StringIO(pred_str)
        csv = pd.read_csv(f, names=gm.ATTRS, header=None, na_values=["nan", "?"])
        x = csv.transpose().to_dict().values()
        context['prediction'] = self.pipeline.predict(x)[0]
        return context


class RepositoryListView(ListView):
    model = Repository


def status_json(request):
    values = []
    repos = Repository.objects.all()
    for repo in repos:
        values.append({"name": repo.full_name, "status": repo.fresh, "url": repo.get_absolute_url(),
                       "id": repo.id_name})
    return JsonResponse(values, safe=False)


def get_repo_commits(request, pk):
    commits = CommitCount.objects.filter(repository__pk=pk)
    today = datetime.date.today()
    if len(commits) != 0:
        first_day = commits[0].date
        iterate_day = first_day
        one_day_more = datetime.timedelta(days=1)
        commits_json = []
        for commit in commits:
            while iterate_day != commit.date:
                commits_json.append({
                    "count": 0,
                    "date": iterate_day.isoformat(),
                    "distance": (iterate_day - first_day).days
                })
                iterate_day += one_day_more
            commits_json.append({
                "count": commit.count,
                "date": commit.date.isoformat(),
                "distance": (commit.date - first_day).days
            })
            iterate_day += one_day_more
        while iterate_day != today:
            commits_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
    else:
        commits_json = []
    return JsonResponse(commits_json, safe=False)


def get_repo_issues(request, pk):
    issues = IssuesCount.objects.filter(repository__pk=pk)
    closedissues = ClosedIssuesCount.objects.filter(repository__pk=pk)
    closedissuestime = ClosedIssuesTime.objects.filter(repository__pk=pk)
    today = datetime.date.today()
    if len(issues) != 0:
        first_day = issues[0].date
        iterate_day = first_day
        one_day_more = datetime.timedelta(days=1)
        issues_json = []
        for issue in issues:
            while iterate_day != issue.date:
                issues_json.append({
                    "count": 0,
                    "date": iterate_day.isoformat(),
                    "distance": (iterate_day - first_day).days
                })
                iterate_day += one_day_more
            issues_json.append({
                "count": issue.count,
                "date": issue.date.isoformat(),
                "distance": (issue.date - first_day).days
            })
            iterate_day += one_day_more
        while iterate_day != today:
            issues_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
        iterate_day = first_day
        closedissues_json = []
        for issue in closedissues:
            while iterate_day != issue.date:
                closedissues_json.append({
                    "count": 0,
                    "date": iterate_day.isoformat(),
                    "distance": (iterate_day - first_day).days
                })
                iterate_day += one_day_more
            closedissues_json.append({
                "count": issue.count,
                "date": issue.date.isoformat(),
                "distance": (issue.date - first_day).days
            })
            iterate_day += one_day_more
        while iterate_day != today:
            closedissues_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
        iterate_day = first_day
        closedissuestime_json = []
        for issuetime in closedissuestime:
            while iterate_day != issuetime.date:
                closedissuestime_json.append({
                    "count": 0,
                    "date": iterate_day.isoformat(),
                    "distance": (iterate_day - first_day).days
                })
                iterate_day += one_day_more
            closedissuestime_json.append({
                "count": issuetime.count,
                "date": issuetime.date.isoformat(),
                "distance": (issuetime.date - first_day).days
            })
            iterate_day += one_day_more
        while iterate_day != today:
            closedissuestime_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
    else:
        issues_json = []
        closedissues_json = []
        closedissuestime_json = []
    response = {"issues": issues_json, "closed_issues": closedissues_json, "closed_time": closedissuestime_json}
    return JsonResponse(response, safe=False)


def get_repo_pulls(request, pk):
    pulls = PullsCount.objects.filter(repository__pk=pk)
    closedpulls = ClosedPullsCount.objects.filter(repository__pk=pk)
    closedpullstime = ClosedPullsTime.objects.filter(repository__pk=pk)
    today = datetime.date.today()
    if len(pulls) != 0:
        first_day = pulls[0].date
        iterate_day = first_day
        one_day_more = datetime.timedelta(days=1)
        pulls_json = []
        for pull in pulls:
            while iterate_day != pull.date:
                pulls_json.append({
                    "count": 0,
                    "date": iterate_day.isoformat(),
                    "distance": (iterate_day - first_day).days
                })
                iterate_day += one_day_more
            pulls_json.append({
                "count": pull.count,
                "date": pull.date.isoformat(),
                "distance": (pull.date - first_day).days
            })
            iterate_day += one_day_more
        while iterate_day != today:
            pulls_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
        iterate_day = first_day
        closedpulls_json = []
        for pull in closedpulls:
            while iterate_day != pull.date:
                closedpulls_json.append({
                    "count": 0,
                    "date": iterate_day.isoformat(),
                    "distance": (iterate_day - first_day).days
                })
                iterate_day += one_day_more
            closedpulls_json.append({
                "count": pull.count,
                "date": pull.date.isoformat(),
                "distance": (pull.date - first_day).days
            })
            iterate_day += one_day_more
        while iterate_day != today:
            closedpulls_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
        iterate_day = first_day
        closedpullstime_json = []
        for pulltime in closedpullstime:
            while iterate_day != pulltime.date:
                closedpullstime_json.append({
                    "count": 0,
                    "date": iterate_day.isoformat(),
                    "distance": (iterate_day - first_day).days
                })
                iterate_day += one_day_more
            closedpullstime_json.append({
                "count": pulltime.count,
                "date": pulltime.date.isoformat(),
                "distance": (pulltime.date - first_day).days
            })
            iterate_day += one_day_more
        while iterate_day != today:
            closedpullstime_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
    else:
        pulls_json = []
        closedpulls_json = []
        closedpullstime_json = []
    response = {"pulls": pulls_json, "closed_pulls": closedpulls_json, "closed_time": closedpullstime_json}
    return JsonResponse(response, safe=False)


def get_repo_forks(request, pk):
    forks = ForksCount.objects.filter(repository__pk=pk)
    today = datetime.date.today()
    if len(forks) != 0:
        first_day = forks[0].date
        iterate_day = first_day
        one_day_more = datetime.timedelta(days=1)
        forks_json = []
        for forks in forks:
            while iterate_day != forks.date:
                forks_json.append({
                    "count": 0,
                    "date": iterate_day.isoformat(),
                    "distance": (iterate_day - first_day).days
                })
                iterate_day += one_day_more
            forks_json.append({
                "count": forks.count,
                "date": forks.date.isoformat(),
                "distance": (forks.date - first_day).days
            })
            iterate_day += one_day_more
        while iterate_day != today:
            forks_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
    else:
        forks_json = []
    return JsonResponse(forks_json, safe=False)
