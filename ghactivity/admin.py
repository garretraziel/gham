from django.contrib import admin
from .models import Repository, CommitCount, IssuesCount, ClosedIssuesCount, ClosedIssuesTime, PullsCount, \
    ClosedPullsCount, ClosedPullsTime, ForksCount


class CommitCountInline(admin.TabularInline):
    model = CommitCount


class IssuesCountInline(admin.TabularInline):
    model = IssuesCount


class ClosedIssuesCountInline(admin.TabularInline):
    model = ClosedIssuesCount


class ClosedIssuesTimeInline(admin.TabularInline):
    model = ClosedIssuesTime


class PullsCountInline(admin.TabularInline):
    model = PullsCount


class ClosedPullsCountInline(admin.TabularInline):
    model = ClosedPullsCount


class ClosedPullsTimeInline(admin.TabularInline):
    model = ClosedPullsTime


class ForksCountInline(admin.TabularInline):
    model = ForksCount


class RepositoryAdmin(admin.ModelAdmin):
    inlines = [
        CommitCountInline,
        IssuesCountInline,
        ClosedIssuesCountInline,
        ClosedIssuesTimeInline,
        PullsCountInline,
        ClosedPullsCountInline,
        ClosedPullsTimeInline,
        ForksCountInline
    ]

    list_display = ('full_name', 'fork', 'fresh', 'obtained')
    list_filter = ('obtained', 'first_commit', 'last_commit', 'fresh')


admin.site.register(Repository, RepositoryAdmin)