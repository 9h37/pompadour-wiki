# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

from pompadour_wiki.views import home, search

urlpatterns = patterns('',
    url(r'^$', home, name='home'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),

    url(r'^accounts/', include('pompadour_wiki.apps.auth.urls')),
    url(r'^wiki/', include('pompadour_wiki.apps.wiki.urls')),
    url(r'^files/', include('pompadour_wiki.apps.filemanager.urls')),
    url(r'^tag/', include('pompadour_wiki.apps.tagging.urls')),

    url(r'search$', search, name='search'),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
