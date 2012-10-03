from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from StringIO import StringIO
from gitdb import IStream
from git import *

from wiki.git_db import Repository
from wiki.models import Wiki, Document

import simplejson as json

import os

def login_failed(request, message, status=None, template_name=None, exception=None):
    data = {
        'error': message
    }

    return render_to_response(u'home.html', data, context_instance=RequestContext(request))

@login_required
def home(request):
    data = {}

    if request.method == 'POST':
        wiki_name = request.POST['add-wiki-name']
        wiki_slug = slugify(wiki_name)
        wiki_desc = request.POST['add-wiki-desc']
        wiki_gitd = '/'.join([settings.WIKI_GIT_DIR, wiki_slug])

        # Check if the slug is present or not
        try:
            w = Wiki.objects.get(slug=wiki_slug)

            data['error'] = 'Can\'t add wiki, another wiki with the same name ({0}) already exists'.format(wiki_name)

        except Wiki.DoesNotExist:
            # Create repository
            repo = Repo.init(wiki_gitd)

            # Add first wiki file
            stream = StringIO('# {0}'.format(wiki_name))
            stream.seek(0, 2)
            streamlen = stream.tell()
            stream.seek(0)

            istream = IStream("blob", streamlen, stream)

            repo.odb.store(istream)

            blob = Blob(repo, istream.binsha, 0100644, 'Home.md')

            repo.index.add([IndexEntry.from_blob(blob)])
            repo.index.commit('Initialize {0}'.format(wiki_name))

            # Create wiki
            wiki = Wiki()
            wiki.name = wiki_name
            wiki.slug = wiki_slug
            wiki.description = wiki_desc
            wiki.gitdir = wiki_gitd
            wiki.save()

    wikis = Wiki.objects.all()

    data['wikis'] = [wikis[x:x+3] for x in xrange(0, len(wikis), 3)]

    return render_to_response(u'home.html', data, context_instance=RequestContext(request))

def _postdoc(request, is_image):
    docpath = u'{0}/{1}'.format(
            settings.MEDIA_ROOT,
            is_image and u'images' or u'documents'
    )

    if not os.path.exists(docpath):
        os.mkdir(docpath)

    f = request.FILES[u'file']

    fd = open(u'{0}/{1}'.format(docpath, f.name), u'wb+')
    for chunk in f.chunks():
        fd.write(chunk)
    fd.close()

    url = u'{0}/{1}/{2}'.format(
            settings.MEDIA_URL,
            is_image and u'images' or u'documents',
            f.name
    )

    try:
        doc = Document.objects.get(path=url)
    except Document.DoesNotExist:
        doc = Document()

        doc.is_image = is_image
        doc.path = url

        doc.wikipath = request.POST[u'page']
        doc.save()

    return HttpResponse(doc.path)

@login_required
def post_img(request):
    if request.method == u'POST':
        return _postdoc(request, True)

@login_required
def post_doc(request):
    if request.method == u'POST':
        return _postdoc(request, False)
