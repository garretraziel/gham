from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render_to_response, render
from django.views.generic import DetailView, ListView, DeleteView
from django.template.context_processors import csrf
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

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

from .models import Repository, CommitCount, IssuesCount, ClosedIssuesCount, ClosedIssuesTime, PullsCount, \
    ClosedPullsCount, ClosedPullsTime, ForksCount


# create entries for series of events in time
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


# create entries for series of events in time, averaging values for each timestamp
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


# download all necessary information from repository for prediction
# this is run in thread
def download_repo_info(gh, owner, name, repository, refresh=False):
    commits, issues, pulls, forks, time_created, time_ended, contributors, predict, = gm.get_repo_stats(gh, owner, name,
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

    # if user is only refreshing set fresh=False before updating values in db
    if refresh:
        repository.fresh = False
        repository.save()

        repository.commitcount_set.all().delete()
        repository.issuescount_set.all().delete()
        repository.closedissuescount_set.all().delete()
        repository.closedissuestime_set.all().delete()
        repository.pullscount_set.all().delete()
        repository.closedpullscount_set.all().delete()
        repository.closedpullstime_set.all().delete()
        repository.forkscount_set.all().delete()

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

    repository.obtained = datetime.date.today()
    repository.fresh = True
    repository.save()


# on get - display form for entering repository name
# on post - start downloading info about repo in another thread
@login_required(login_url='/')
def get_repo_info(request):
    if request.method == 'GET':
        c = {}
        c.update(csrf(request))
        return render_to_response("ghactivity/repository_get.html", c)
    elif request.method == 'POST':
        full_name = request.POST['repository']
        owner, name = full_name.split("/", 1)

        # try to find this repo in database
        existing = Repository.objects.filter(owner=owner, name=name)
        if existing.exists():
            r = existing.get()
            if not r.accessible_by.filter(pk=request.user.pk).exists():
                r.accessible_by.add(request.user)
                r.save()
            return redirect("repo_list")

        # get object for accessing github API
        token = request.user.social_auth.filter(provider='github').first().extra_data['access_token']
        gh = github.GitHub(access_token=token)

        # get basic info - name etc.
        try:
            rid, full_name, fork, created_at, forked_from = gm.get_basic_repo_info(gh, owner, name)
        except github.ApiNotFoundError:
            raise Http404("No such repo exists.")

        # save basic info to db
        r = Repository(repository_id=rid, owner=owner, name=name, fork=forked_from)
        r.save()
        r.accessible_by.add(request.user)
        r.save()

        # start thread for downloading additional info
        t = threading.Thread(target=download_repo_info, args=(gh, owner, name, r))
        t.start()

        return redirect("repo_list")


@login_required(login_url='/')
def update_repository(request, pk):
    r = get_object_or_404(request.user.access, pk=pk)

    token = request.user.social_auth.filter(provider='github').first().extra_data['access_token']
    gh = github.GitHub(access_token=token)

    # stat thread for downloading new info
    t = threading.Thread(target=download_repo_info, args=(gh, r.owner, r.name, r, True))
    t.start()

    return redirect("repo_list")


class RepositoryDetail(DetailView):
    @classmethod
    def load_clf(cls, datasetname):
        # load dataset, train model
        this_dir = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(this_dir, "datasets/%s" % datasetname)
        modelname = os.path.join(this_dir, "models/%s.pkl" % datasetname)
        if os.path.exists(modelname):  # try to load serialized model
            cls.pipeline = joblib.load(modelname)
            return

        # there is no serialized model, train new model
        # read dataset
        csv = pd.read_csv(filename, na_values=["nan", "?"])
        x_csv = csv.iloc[:, :-1].copy()
        y_csv = csv['result'].copy()
        x = x_csv.transpose().to_dict().values()
        y = y_csv.as_matrix()

        # create pipeline of vectorizer, imputer and regressor
        v = DictVectorizer(sparse=False)
        i = Imputer()
        clf = GradientBoostingRegressor()
        cls.pipeline = Pipeline([('vectorizer', v), ('imputer', i), ('regressor', clf)])
        cls.pipeline.fit(x, y)
        # serialize into file
        joblib.dump(cls.pipeline, modelname)

    def get_queryset(self):
        return self.request.user.access.all()

    def get_context_data(self, **kwargs):
        # get repository
        context = super(RepositoryDetail, self).get_context_data(**kwargs)
        # get prediction string
        pred_str = context['repository'].prediction_string
        # parse prediction string
        f = StringIO(pred_str)
        csv = pd.read_csv(f, names=gm.ATTRS, header=None, na_values=["nan", "?"])
        x = csv.transpose().to_dict().values()
        # predict values
        context['prediction'] = self.pipeline.predict(x)[0]
        context['repository_list'] = self.request.user.access.all()
        pk = context['repository'].pk
        context['badge_url'] = self.request.build_absolute_uri(reverse("repo_badge", kwargs={"pk": pk}))
        context['index_url'] = self.request.build_absolute_uri(reverse("index"))
        return context

    @method_decorator(login_required(login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(RepositoryDetail, self).dispatch(*args, **kwargs)


class RepositoryListView(ListView):
    @method_decorator(login_required(login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(RepositoryListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return self.request.user.access.all()

    def get_context_data(self, **kwargs):
        context = super(RepositoryListView, self).get_context_data(**kwargs)
        context['user'] = {"username": self.request.user.username,
                           "repos_count": self.request.user.access.all().count()}
        return context


class DeleteRepositoryView(DeleteView):
    model = Repository
    success_url = reverse_lazy("repo_list")

    @method_decorator(login_required(login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(DeleteRepositoryView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(DeleteRepositoryView, self).get_object()
        if obj.accessible_by.filter(pk=self.request.user.pk).exists():
            return obj
        raise Http404

    def delete(self, request, *args, **kwargs):
        # unregister user from repo.accessible_by
        self.object = self.get_object()
        self.object.accessible_by.remove(request.user)
        # if there is no other user in accessible_by, remove repo completely
        if self.object.accessible_by.count() == 0:
            self.object.delete()
        return HttpResponseRedirect(self.get_success_url())


# AJAX: return JSON response about repos status
@login_required(login_url='/')
def status_json(request):
    values = []
    repos = request.user.access.all()
    for repo in repos:
        values.append({"name": repo.full_name, "status": repo.fresh, "url": repo.get_absolute_url(),
                       "id": repo.id_name})
    return JsonResponse(values, safe=False)


# AJAX: return JSON response containing all info about commits
@login_required(login_url='/')
def get_repo_commits(request, pk):
    repository = get_object_or_404(request.user.access, pk=pk)
    commits = CommitCount.objects.filter(repository=repository)
    today = datetime.date.today()
    count = 0
    # JSONify response. put count: 0 to days without commit
    if len(commits) != 0:
        first_day = commits[0].date
        iterate_day = first_day
        one_day_more = datetime.timedelta(days=1)
        commits_json = []
        for commit in commits:
            while iterate_day < commit.date:
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
            count += commit.count
            iterate_day += one_day_more
        while iterate_day < today:
            commits_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
    else:
        commits_json = []
    result = {'count': count, 'commits': commits_json}
    return JsonResponse(result, safe=False)


# AJAX: return JSON response containing all info about issues
@login_required(login_url='/')
def get_repo_issues(request, pk):
    repository = get_object_or_404(request.user.access, pk=pk)
    issues = IssuesCount.objects.filter(repository=repository)
    closedissues = ClosedIssuesCount.objects.filter(repository=repository)
    closedissuestime = ClosedIssuesTime.objects.filter(repository=repository)
    today = datetime.date.today()
    issues_count = 0
    closed_count = 0
    # JSONify response. put count: 0 to days without issue
    if len(issues) != 0:
        first_day = issues[0].date
        iterate_day = first_day
        one_day_more = datetime.timedelta(days=1)
        issues_json = []
        for issue in issues:
            while iterate_day < issue.date:
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
            issues_count += issue.count
            iterate_day += one_day_more
        while iterate_day < today:
            issues_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
        iterate_day = first_day
        closedissues_json = []
        for issue in closedissues:
            while iterate_day < issue.date:
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
            closed_count += issue.count
            iterate_day += one_day_more
        while iterate_day < today:
            closedissues_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
        iterate_day = first_day
        closedissuestime_json = []
        for issuetime in closedissuestime:
            while iterate_day < issuetime.date:
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
        while iterate_day < today:
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
    response = {"issues": issues_json, "closed_issues": closedissues_json, "closed_time": closedissuestime_json,
                "issues_count": issues_count, "closed_count": closed_count}
    return JsonResponse(response, safe=False)


# AJAX: return JSON response containing all info about pull requests
@login_required(login_url='/')
def get_repo_pulls(request, pk):
    repository = get_object_or_404(request.user.access, pk=pk)
    pulls = PullsCount.objects.filter(repository=repository)
    closedpulls = ClosedPullsCount.objects.filter(repository=repository)
    closedpullstime = ClosedPullsTime.objects.filter(repository=repository)
    today = datetime.date.today()
    pulls_count = 0
    closed_count = 0
    # JSONify response. put count: 0 to days without pull request
    if len(pulls) != 0:
        first_day = pulls[0].date
        iterate_day = first_day
        one_day_more = datetime.timedelta(days=1)
        pulls_json = []
        for pull in pulls:
            while iterate_day < pull.date:
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
            pulls_count += pull.count
            iterate_day += one_day_more
        while iterate_day < today:
            pulls_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
        iterate_day = first_day
        closedpulls_json = []
        for pull in closedpulls:
            while iterate_day < pull.date:
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
            closed_count += pull.count
            iterate_day += one_day_more
        while iterate_day < today:
            closedpulls_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
        iterate_day = first_day
        closedpullstime_json = []
        for pulltime in closedpullstime:
            while iterate_day < pulltime.date:
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
        while iterate_day < today:
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
    response = {"pulls": pulls_json, "closed_pulls": closedpulls_json, "closed_time": closedpullstime_json,
                "pulls_count": pulls_count, "closed_count": closed_count}
    return JsonResponse(response, safe=False)


# AJAX: return JSON response containing all info about forks
@login_required(login_url='/')
def get_repo_forks(request, pk):
    repository = get_object_or_404(request.user.access, pk=pk)
    forks = ForksCount.objects.filter(repository=repository)
    today = datetime.date.today()
    count = 0
    # JSONify response. put count: 0 to days without forks
    if len(forks) != 0:
        first_day = forks[0].date
        iterate_day = first_day
        one_day_more = datetime.timedelta(days=1)
        forks_json = []
        for forks in forks:
            while iterate_day < forks.date:
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
            count += forks.count
            iterate_day += one_day_more
        while iterate_day < today:
            forks_json.append({
                "count": 0,
                "date": iterate_day.isoformat(),
                "distance": (iterate_day - first_day).days
            })
            iterate_day += one_day_more
    else:
        forks_json = []
    result = {"count": count, "forks": forks_json}
    return JsonResponse(result, safe=False)


# render badge - use SVG template
def get_repo_badge(request, pk):
    repo = get_object_or_404(Repository, pk=pk)
    # make prediction
    pred_str = repo.prediction_string
    f = StringIO(pred_str)
    csv = pd.read_csv(f, names=gm.ATTRS, header=None, na_values=["nan", "?"])
    x = csv.transpose().to_dict().values()
    prediction = RepositoryDetail.pipeline.predict(x)[0]
    return render(request, "ghactivity/activity.svg", {"prediction": prediction}, content_type="image/svg+xml")
