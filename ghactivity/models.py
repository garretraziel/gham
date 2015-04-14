from django.db import models
from django.conf import settings
from urlparse import urljoin


class Repository(models.Model):
    repository_id = models.IntegerField(primary_key=True)
    owner = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    fork = models.CharField(max_length=500, null=True, blank=True)
    first_commit = models.DateField()
    last_commit = models.DateField()

    def _get_full_name(self):
        return "%s/%s" % (self.owner, self.name)
    full_name = property(_get_full_name)

    def _get_github_url(self):
        return urljoin(settings.GITHUB_URL, self.full_name)
    github_url = property(_get_github_url)

    def __unicode__(self):
        return self.full_name

    class Meta:
        ordering = ['-repository_id']
        verbose_name_plural = "repositories"
        unique_together = (('owner', 'name'),)


class CommitCount(models.Model):
    count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class IssuesCount(models.Model):
    issues_count = models.IntegerField()
    closed_count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class IssuesTime(models.Model):
    issues_time = models.FloatField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class PullsCount(models.Model):
    pulls_count = models.IntegerField()
    closed_count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class ClosedPullsTime(models.Model):
    time_to_close = models.FloatField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class ContribCount(models.Model):
    count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class ForksCount(models.Model):
    count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)
