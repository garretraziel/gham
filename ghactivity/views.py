from django.shortcuts import render_to_response
from django.views.generic import DetailView, ListView
from django.template.context_processors import csrf
from django.shortcuts import redirect
from django.http import Http404
from django.conf import settings

from datetime import date
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

from .models import Repository, Author, CommitCount, IssuesCount, ClosedIssuesCount, ClosedIssuesTime, PullsCount, \
    ClosedPullsCount, ClosedPullsTime, ForksCount


def _create_count_series(values, get_date, obj, repository):
    if len(values) != 0:
        t_date = get_date(values[0])
        count = 0
        for value in values:
            if get_date(value) == t_date:
                count += 1
            else:
                obj.objects.create(count=count, date=t_date, repository=repository)
                t_date = get_date(value)
                count = 1
        obj.objects.create(count=count, date=t_date, repository=repository)


def _create_average_series(values, get_date, get_value, obj, repository):
    if len(values) != 0:
        t_date = get_date(values[0])
        count = 0
        s = 0.0
        for value in values:
            if get_date(value) == t_date:
                count += 1
                s += get_value(value)
            else:
                avg = s / count
                obj.objects.create(avg=avg, date=t_date, repository=repository)
                t_date = get_date(value)
                count = 1
                s = 0.0
        avg = s / count
        obj.objects.create(avg=avg, date=t_date, repository=repository)


def _download_repo_info(owner, name, fork, repository):
    gh = github.GitHub(username=settings.GITHUB_USERNAME,
                       password=settings.GITHUB_PASSWORD)

    values = []
    now = date.today()

    commits, time_created, time_ended = gm.get_all_commits(gh, owner, name)
    values.extend(gm.get_commits_stats(commits, time_created, now))

    issues, pulls = gm.get_all_issues_pulls(gh, owner, name)
    values.extend(gm.get_issues_stats(issues, time_created, now))
    values.extend(gm.get_issues_stats(pulls, time_created, now))

    try:
        events = gm.get_all_events(gh, owner, name)
        values.extend(gm.get_events_stats(events, time_created, now))
    except github.ApiError:
        # toto cas od casu selze, protoze GitHub nechce poskytovat velkou spoustu stranek
        values.extend(["nan"] * 6)

    values.extend(gm.get_contributors_stats(commits, time_created, now))

    ccomments = gm.get_all_commit_comments(gh, owner, name)
    values.extend(gm.get_commit_comments_stats(ccomments, time_created, now))

    forks = gm.get_all_forks(gh, owner, name)
    values.extend(gm.get_forks_stats(forks, time_created, now))

    duration = (now - time_created).days + 1
    values.append(str(duration))
    values.append(str(fork))

    contributors = gm.get_contributors_stats(commits, time_created, now)
    contributors = contributors[0] + contributors[1]

    prediction_string = ",".join(values)

    repository.first_commit = time_created
    repository.last_commit = time_ended
    repository.contributors = contributors
    repository.prediction_string = prediction_string

    issues = [issue for issue, _ in issues]
    pulls = [pull for pull, _ in pulls]

    commits.sort(key=gm.get_commit_date)
    issues.sort(key=gm.get_direct_date)
    pulls.sort(key=gm.get_direct_date)
    forks.sort(key=gm.get_direct_date)

    _create_count_series(commits, gm.get_commit_date, CommitCount, repository)

    _create_count_series(issues, gm.get_direct_date, IssuesCount, repository)
    issues = [issue for issue in issues if issue['state'] == 'closed']
    issues.sort(key=gm.get_close_date)
    _create_count_series(issues, gm.get_close_date, ClosedIssuesCount, repository)
    _create_average_series(issues, gm.get_close_date, gm.get_time_to_close, ClosedIssuesTime, repository)

    _create_count_series(pulls, gm.get_direct_date, PullsCount, repository)
    pulls = [pull for pull in pulls if pull['state'] == 'closed']
    pulls.sort(key=gm.get_close_date)
    _create_count_series(pulls, gm.get_close_date, ClosedPullsCount, repository)
    _create_average_series(pulls, gm.get_close_date, gm.get_time_to_close, ClosedPullsTime, repository)

    _create_count_series(forks, gm.get_direct_date, ForksCount, repository)

    repository.fresh = True
    repository.save()


def get_repo_info(request):
    if request.method == 'GET':
        c = {}
        c.update(csrf(request))
        return render_to_response("ghactivity/index.html", c)
    elif request.method == 'POST':
        full_name = request.POST['repository']
        owner, name = full_name.split("/", 1)

        author, _ = Author.objects.get_or_create(name=owner)

        if Repository.objects.filter(owner__pk=author.pk).filter(name=name).count() != 0:
            r = Repository.objects.filter(owner__pk=author.pk).filter(name=name).get()
            return redirect("repo_detail", pk=r.pk)

        gh = github.GitHub(username=settings.GITHUB_USERNAME,
                           password=settings.GITHUB_PASSWORD)

        try:
            rid, full_name, fork, created_at = gm.get_basic_repo_info(gh, owner, name)
        except github.ApiNotFoundError:
            raise Http404("No such repo exists.")

        r = Repository(repository_id=rid, owner=author, name=name, fork=str(fork))
        r.save()

        t = threading.Thread(target=_download_repo_info, args=(owner, name, fork, r))
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
        X_csv = csv.iloc[:, :-1].copy()
        y_csv = csv['result'].copy()
        X = X_csv.transpose().to_dict().values()
        y = y_csv.as_matrix()

        v = DictVectorizer(sparse=False)
        i = Imputer()
        clf = GradientBoostingRegressor()
        cls.pipeline = Pipeline([('vectorizer', v), ('imputer', i), ('regressor', clf)])
        cls.pipeline.fit(X, y)
        joblib.dump(cls.pipeline, modelname)

    def get_context_data(self, **kwargs):
        context = super(RepositoryDetail, self).get_context_data(**kwargs)
        pred_str = context['repository'].prediction_string
        f = StringIO(pred_str)
        csv = pd.read_csv(f, names=gm.ATTRS, header=None, na_values=["nan", "?"])
        X = csv.transpose().to_dict().values()
        context['prediction'] = self.pipeline.predict(X)
        return context


class RepositoryListView(ListView):
    model = Repository