from django.contrib import admin
from .models import Repository, CommitCount


class CommitCountInline(admin.TabularInline):
    model = CommitCount


class RepositoryAdmin(admin.ModelAdmin):
    inlines = [
        CommitCountInline,
    ]
admin.site.register(Repository, RepositoryAdmin)