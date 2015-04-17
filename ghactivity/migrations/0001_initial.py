# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ClosedIssuesCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='ClosedIssuesTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.FloatField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='ClosedPullsCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='ClosedPullsTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.FloatField()),
                ('date', models.DateField()),
            ],
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
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('repository_id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('fork', models.CharField(max_length=500, null=True, blank=True)),
                ('first_commit', models.DateField(default=datetime.date.today)),
                ('last_commit', models.DateField(default=datetime.date.today)),
                ('contributors', models.IntegerField(default=0)),
                ('fresh', models.BooleanField(default=False)),
                ('prediction_string', models.TextField(default=b'0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', validators=[django.core.validators.RegexValidator(regex=b'([^,]+(,|$)){89}')])),
                ('owner', models.ForeignKey(to='ghactivity.Author')),
            ],
            options={
                'ordering': ['-repository_id'],
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
            name='issuescount',
            unique_together=set([('date', 'repository')]),
        ),
        migrations.AlterUniqueTogether(
            name='commitcount',
            unique_together=set([('date', 'repository')]),
        ),
    ]
