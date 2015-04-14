# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClosedPullsTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_to_close', models.FloatField()),
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
        ),
        migrations.CreateModel(
            name='ContribCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('count', models.IntegerField()),
                ('date', models.DateField()),
            ],
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
                ('issues_count', models.IntegerField()),
                ('closed_count', models.IntegerField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='IssuesTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('issues_time', models.FloatField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='PullsCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pulls_count', models.IntegerField()),
                ('closed_count', models.IntegerField()),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('repository_id', models.IntegerField(serialize=False, primary_key=True)),
                ('owner', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('fork', models.CharField(max_length=500, null=True, blank=True)),
                ('first_commit', models.DateField()),
                ('last_commit', models.DateField()),
            ],
            options={
                'ordering': ['-repository_id'],
                'verbose_name_plural': 'repositories',
            },
        ),
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together=set([('owner', 'name')]),
        ),
        migrations.AddField(
            model_name='pullscount',
            name='repository',
            field=models.ForeignKey(to='ghactivity.Repository'),
        ),
        migrations.AddField(
            model_name='issuestime',
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
            model_name='contribcount',
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
    ]
