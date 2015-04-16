from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from urlparse import urljoin
from datetime import date


class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name


class Repository(models.Model):
    repository_id = models.IntegerField(primary_key=True)
    owner = models.ForeignKey(Author)
    name = models.CharField(max_length=255)
    fork = models.CharField(max_length=500, null=True, blank=True)
    first_commit = models.DateField(default=date.today)
    last_commit = models.DateField(default=date.today)
    contributors = models.IntegerField(default=0)
    fresh = models.BooleanField(default=False)
    prediction_string = models.TextField(validators=[
        RegexValidator(regex=r'([^,]+(,|$)){89}')
    ], default=",".join(["0"]*89))

    def _get_full_name(self):
        return "%s/%s" % (self.owner, self.name)
    full_name = property(_get_full_name)

    def _get_id_name(self):
        return "%s_%s" % (self.owner, self.name)
    id_name = property(_get_id_name)

    def _get_github_url(self):
        return urljoin(settings.GITHUB_URL, self.full_name)
    github_url = property(_get_github_url)

    def __unicode__(self):
        return self.full_name

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('repo_detail', kwargs={"pk": self.pk})

    class Meta:
        ordering = ['-repository_id']
        verbose_name_plural = "repositories"
        unique_together = (('owner', 'name'),)


class CommitCount(models.Model):
    count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)

    def __unicode__(self):
        return "%s for %s" % (self.repository.full_name, self.date.isoformat())

    class Meta:
        ordering = ['date']
        verbose_name_plural = "commit counts"
        unique_together = (('date', 'repository'),)


class IssuesCount(models.Model):
    count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)

    def __unicode__(self):
        return "%s for %s" % (self.repository.full_name, self.date.isoformat())

    class Meta:
        ordering = ['date']
        verbose_name_plural = "issues counts"
        unique_together = (('date', 'repository'),)


class ClosedIssuesCount(models.Model):
    count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class ClosedIssuesTime(models.Model):
    count = models.FloatField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class PullsCount(models.Model):
    count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class ClosedPullsCount(models.Model):
    count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class ClosedPullsTime(models.Model):
    count = models.FloatField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)


class ForksCount(models.Model):
    count = models.IntegerField()
    date = models.DateField()
    repository = models.ForeignKey(Repository)
