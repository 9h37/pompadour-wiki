# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns

from pompadour_wiki.apps.filemanager.views import get_mimetype_image, index, view_document, upload_document

urlpatterns = patterns('',
        url(r'^type/(?P<mimetype>[-\w\./]+)$', get_mimetype_image, name='filemanager-get-type'),
        url(r'^(?P<wiki>[^/]+)/view/(?P<path>.+)$', view_document, name='filemanager-view'),
        url(r'^(?P<wiki>[^/]+)/tree/(?P<path>.*)$', index, name='filemanager-index'),
        url(r'^(?P<wiki>[^/]+)/upload$', upload_document, name='filemanager-upload'),
)