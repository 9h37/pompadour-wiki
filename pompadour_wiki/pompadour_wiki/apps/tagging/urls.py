# -*- coding: utf-8 -*-


from django.conf.urls import url, patterns

from pompadour_wiki.apps.tagging.views import view_tag

urlpatterns = patterns('',
        url(r'^(?P<tagname>.+)$', view_tag, name='view-tag'),
)

