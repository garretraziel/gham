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

    predict_names = ["commits_count", "commits_f_1w", "commits_f_1m", "commits_f_6m", "commits_f_1y", "commits_f_all",
                     "issues_count", "issues_f_1w", "issues_f_1m", "issues_f_6m", "issues_f_1y", "issues_f_all",
                     "closed_issues_count", "closed_issues_f_1w", "closed_issues_f_1m", "closed_issues_f_6m",
                     "closed_issues_f_1y", "closed_issues_f_all", "closed_issues_time_1w", "closed_issues_time_1m",
                     "closed_issues_time_6m", "closed_issues_time_1y", "closed_issues_time_all", "comments_count",
                     "comments_f_1w", "comments_f_1m", "comments_f_6m", "comments_f_1y", "comments_f_all",
                     "pulls_count", "pulls_f_1w", "pulls_f_1m", "pulls_f_6m", "pulls_f_1y", "pulls_f_all",
                     "closed_pulls_count", "closed_pulls_f_1w", "closed_pulls_f_1m", "closed_pulls_f_6m",
                     "closed_pulls_f_1y", "closed_pulls_f_all", "closed_pulls_time_1w", "closed_pulls_time_1m",
                     "closed_pulls_time_6m", "closed_pulls_time_1y", "closed_pulls_time_all", "pulls_comments_count",
                     "pulls_comments_f_1w", "pulls_comments_f_1m", "pulls_comments_f_6m", "pulls_comments_f_1y",
                     "pulls_comments_f_all", "events_count", "events_f_1w", "events_f_1m", "events_f_6m", "events_f_1y",
                     "events_f_all", "contrib_count", "contrib_others", "contrib_p25_1w", "contrib_p50_1w",
                     "contrib_p75_1w", "contrib_p25_1m", "contrib_p50_1m", "contrib_p75_1m", "contrib_p25_6m",
                     "contrib_p50_6m", "contrib_p75_6m", "contrib_p25_1y", "contrib_p50_1y", "contrib_p75_1y",
                     "contrib_p25_all", "contrib_p50_all", "contrib_p75_all", "ccomments_count", "ccomments_f_1w",
                     "ccomments_f_1m", "ccomments_f_6m", "ccomments_f_1y", "ccomments_f_all", "forks_count",
                     "forks_f_1w", "forks_f_1m", "forks_f_6m", "forks_f_1y", "forks_f_all", "days_active", "fork"]

    @classmethod
    def load_clf(cls, filename):
        csv = pd.read_csv(filename, na_values=["?"])
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
        csv = pd.read_csv(f, names=self.predict_names, header=None)
        csv = csv.replace(-1, pd.np.NaN)
        X = self.v.transform(csv.transpose().to_dict().values())
        X = self.i.transform(X)
        context['prediction'] = self.clf.predict(X)
        return context