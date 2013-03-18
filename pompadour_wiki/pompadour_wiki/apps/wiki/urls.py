# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns

from pompadour_wiki.apps.wiki.views import view_page, edit_page, remove_page

urlpatterns = patterns('',
        url(r'^(?P<wiki>[^/]+)/(?P<path>.+)/edit$', edit_page, name='edit-page'),
        url(r'^(?P<wiki>[^/]+)/(?P<path>.+)/remove$', remove_page, name='remove-page'),
        url(r'^(?P<wiki>[^/]+)/(?P<path>.*)$', view_page, name='view-page'),
)

