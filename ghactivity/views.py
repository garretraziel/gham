from django.shortcuts import render_to_response
from github import GitHub
from ghaminer import ghaminer as gm
from datetime import date


def get_repo_info(request, owner, name):
    gh = GitHub()  # TODO: login
    now = date.today()
    commits = gm.get_all_commits(gh, owner, name)
    #return render_to_response("ghactivity/")
