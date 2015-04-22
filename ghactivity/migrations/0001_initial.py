# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClosedIssuesCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
                'verbose_name_plural': 'closed issues counts',
            },
        ),
        migrations.CreateModel(
            name='ClosedIssuesTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.FloatField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
                'verbose_name_plural': 'closed issue times',
            },
        ),
        migrations.CreateModel(
            name='ClosedPullsCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
                'verbose_name_plural': 'closed pulls counts',
            },
        ),
        migrations.CreateModel(
            name='ClosedPullsTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.FloatField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
                'verbose_name_plural': 'closed pull requests times',
            },
        ),
        migrations.CreateModel(
            name='CommitCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
                'verbose_name_plural': 'commit counts',
            },
        ),
        migrations.CreateModel(
            name='ForksCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
                'verbose_name_plural': 'forks counts',
            },
        ),
        migrations.CreateModel(
            name='IssuesCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
                'verbose_name_plural': 'issues counts',
            },
        ),
        migrations.CreateModel(
            name='PullsCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['date'],
                'verbose_name_plural': 'pulls counts',
            },
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('repository_id', models.IntegerField(serialize=False, primary_key=True)),
                ('owner', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('fork', models.CharField(max_length=500, null=True, blank=True)),
                ('first_commit', models.DateField(default=datetime.date.today)),
                ('last_commit', models.DateField(default=datetime.date.today)),
                ('obtained', models.DateField(default=datetime.date.today)),
                ('contributors', models.IntegerField(default=0)),
                ('fresh', models.BooleanField(default=False)),
                ('prediction_string', models.TextField(default=b'0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', validators=[django.core.validators.RegexValidator(regex=b'([^,]+(,|$)){89}')])),
                ('accessible_by', models.ManyToManyField(related_name='access', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['owner__name', 'name'],
                'verbose_name_plural': 'repositories',
            },
        ),
        migrations.AddField(
            model_name='pullscount',
            name='repository',
            field=models.ForeignKey(to='ghactivity.Repository'),
        ),
        migrations.AddField(
            model_name='issuescount',
            name='repository',
            field=models.ForeignKey(to='ghactivity.Repository'),
        ),
        migrations.AddField(
            model_name='forkscount',
            name='repository',
            field=models.ForeignKey(to='ghactivity.Repository'),
        ),
        migrations.AddField(
            model_name='commitcount',
            name='repository',
            field=models.ForeignKey(to='ghactivity.Repository'),
        ),
        migrations.AddField(
            model_name='closedpullstime',
            name='repository',
            field=models.ForeignKey(to='ghactivity.Repository'),
        ),
        migrations.AddField(
            model_name='closedpullscount',
            name='repository',
            field=models.ForeignKey(to='ghactivity.Repository'),
        ),
        migrations.AddField(
            model_name='closedissuestime',
            name='repository',
            field=models.ForeignKey(to='ghactivity.Repository'),
        ),
        migrations.AddField(
            model_name='closedissuescount',
            name='repository',
            field=models.ForeignKey(to='ghactivity.Repository'),
        ),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together=set([('owner', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='pullscount',
            unique_together=set([('date', 'repository')]),
        ),
        migrations.AlterUniqueTogether(
            name='issuescount',
            unique_together=set([('date', 'repository')]),
        ),
        migrations.AlterUniqueTogether(
            name='forkscount',
            unique_together=set([('date', 'repository')]),
        ),
        migrations.AlterUniqueTogether(
            name='commitcount',
            unique_together=set([('date', 'repository')]),
        ),
        migrations.AlterUniqueTogether(
            name='closedpullstime',
            unique_together=set([('date', 'repository')]),
        ),
        migrations.AlterUniqueTogether(
            name='closedpullscount',
            unique_together=set([('date', 'repository')]),
        ),
        migrations.AlterUniqueTogether(
            name='closedissuestime',
            unique_together=set([('date', 'repository')]),
        ),
        migrations.AlterUniqueTogether(
            name='closedissuescount',
            unique_together=set([('date', 'repository')]),
        ),
    ]
