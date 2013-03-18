# -*- coding: utf-8 -*-

from pompadour_wiki.apps.wiki.models import Wiki, WikiNotifier
from django.contrib import admin

admin.site.register(Wiki)
admin.site.register(WikiNotifier)
