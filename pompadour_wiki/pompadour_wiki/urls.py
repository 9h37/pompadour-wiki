from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'pompadour_wiki.views.home', name='home'),
    url(r'^send/image/$', 'pompadour_wiki.views.post_img', name='post-image'),
    url(r'^send/document/$', 'pompadour_wiki.views.post_doc', name='post-document'),

    url(r'^login/$', 'django_openid_auth.views.login_begin', name='openid-login'),
    url(r'^login-complete/$', 'django_openid_auth.views.login_complete', name='openid-complete'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # MarkItUp
    url(r'^markitup/', include('markitup.urls')),

    url(r'^lock/(?P<lock_id>(\d+))/$', 'lock.views.detail', name='lock'),

    url(r'^tree/(?P<wiki>[^/]+)/$', 'wiki.views.tree', name='tree'),
    url(r'^diff/(?P<wiki>[^/]+)/$', 'wiki.views.diff', name='diff'),
    url(r'^edit/(?P<wiki>[^/]+)/', 'wiki.views.edit', name='edit'),
    url(r'^del/(?P<wiki>[^/]+)/', 'wiki.views.remove', name='remove'),
    url(r'^wiki/(?P<wiki>[^/]+)/', 'wiki.views.page', name='page'),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
