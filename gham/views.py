from django.shortcuts import redirect, render_to_response
from django.contrib.auth import logout


def index(request):
    if request.user.is_authenticated():
        return redirect('repo_list')
    else:
        return render_to_response('index.html')


def logout_user(request):
    logout(request)
    return redirect('/')
