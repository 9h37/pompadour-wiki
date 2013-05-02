# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext
from django.conf import settings

from pompadour_wiki.apps.utils.decorators import render_to, redirect_to
from pompadour_wiki.apps.utils import breadcrumbify, urljoin

from pompadour_wiki.apps.wiki.models import Wiki

from pompadour_wiki.apps.filemanager.forms import UploadDocumentForm

import random
import json
import os


@login_required
def get_mimetype_image(request, mimetype):

    def test_for(mimetype):
        # Get the filename of the mimetype image
        filename = '{0}.png'.format('-'.join(mimetype.split('/')))

        path = os.path.join(settings.STATIC_ROOT, 'img', 'icons', filename)
        url = urljoin(settings.STATIC_URL, 'img', 'icons', filename)

        if os.path.exists(path):
            return redirect(url)

    # Test for the requested mimetype
    result = test_for(mimetype)

    if result:
        return result

    # Test for the generic mimetype
    components = mimetype.split('/')
    components[1] = 'x-generic'
    mimetype = '/'.join(components)

    result = test_for(mimetype)

    if result:
        return result

    # Test for the unknow icon
    result = test_for('unknown')

    if result:
        return result

    # Returns a 404 error
    return HttpResponseNotFound('No image for {0}'.format(mimetype))

@login_required
@render_to('filemanager/index.html')
def index(request, wiki, path):
    w = get_object_or_404(Wiki, slug=wiki)

    attach_page = request.GET.get('attach', settings.WIKI_INDEX)

    if not w.repo.exists(u'{0}.md'.format(attach_page)):
        attach_page = settings.WIKI_INDEX

    filelist = []

    # Get the folder path inside git repository
    if path:
        gitfolder = os.path.join('__media__', path)
    else:
        gitfolder = '__media__'

    # Check if the directory exists
    if w.repo.exists(gitfolder):
        # List directory
        directories, files = w.repo.listdir(gitfolder)

        # Append directories
        for d in directories:
            filelist.append({
                'url': urljoin(path, d.encode('utf-8')),
                'name': d,
                'mimetype': 'inode/directory'
            })

        # Append files
        for f in files:
            filelist.append({
                'url': urljoin(path, f.encode('utf-8')),
                'name': f,
                'mimetype': w.repo.mimetype(os.path.join(gitfolder, f))
            })

    return {'wiki': {
        'files': filelist,
        'obj': w,
        'attach_page': attach_page,
        'breadcrumbs': breadcrumbify(path),
        'forms': {
            'upload': UploadDocumentForm({})
        }
    }}

@login_required
def view_document(request, wiki, path):
    w = get_object_or_404(Wiki, slug=wiki)

    # Get the folder path inside git repository
    if path:
        gitpath = os.path.join('__media__', path)
    else:
        gitpath = '__media__'

    # Check if the path exists
    if not w.repo.exists(gitpath):
        raise Http404

    # Check if the path point to a folder
    if w.repo.is_dir(gitpath):
        return redirect('filemanager-index', wiki, path)

    # Return content
    f = w.repo.open(gitpath)
    content = f.read()
    f.close()

    mimetype = w.repo.mimetype(gitpath)

    return HttpResponse(content, content_type=mimetype)

@login_required
def upload_document(request, wiki):
    w = get_object_or_404(Wiki, slug=wiki)

    if request.method != 'POST':
        raise Http404

    format = request.POST.pop('format', [None])[0]

    form = UploadDocumentForm(request.POST, request.FILES)

    if form.is_valid():
        path = form.cleaned_data['path'].replace('\\', '/')
        path = os.path.join(*path.split('/'))

        doc = request.FILES['doc']

        # Add the file to the repository, save() returns the new file path.
        git_path = os.path.join(path, doc.name)
        doc_path = w.repo.save(git_path, doc)

        w.repo.commit(request.user, ugettext(u'Upload document: {0}').format(path))

        if format == "json":
            data = {
                'url': doc_path,
            }

            return HttpResponse(json.dumps(data))

    return redirect(reverse('filemanager-index', args=[wiki, '']))