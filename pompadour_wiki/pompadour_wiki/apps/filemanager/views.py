# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext
from django.conf import settings

from pompadour_wiki.apps.utils.decorators import render_to, redirect_to
from pompadour_wiki.apps.utils import breadcrumbify, urljoin, logdebug

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

    filelist = []

    # Get the folder path inside git repository
    if path:
        gitfolder = os.path.join('__media__', path)
    else:
        gitfolder = '__media__'

    # Check if the directory exists
    if w.repo.exists(gitfolder):
        # Get file list
        files = w.repo.get_folder_tree(gitfolder)

        # Append files to the list for the view
        for f in files:
            filelist.append({
                'url': urljoin(path, f['name']),
                'name': f['name'],
                'mimetype': f['type']
            })

    return {'wiki': {
        'files': filelist,
        'obj': w,
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
    content = w.repo.get_content(gitpath)

    return HttpResponse(content[0], content_type=content[2])

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

        # Make sure that the filename is unique
        # NB: if we upload the exact same file, it doesn't matter, only one blob
        #     will be stored in the repository.

        doc_name = doc.name
        doc_path = os.path.join(path, doc_name)
        git_path = os.path.join('__media__', doc_path)

        # if the path exists, add a uniqid to the file
        while w.repo.exists(git_path):
            uniqid = str(random.randint(0, 9))

            doc_name = u'{0}{1}'.format(uniqid, doc_name)
            doc_path = os.path.join(path, doc_name)
            git_path = os.path.join('__media__', doc_path)

        # Finally put file into the Git repository

        os.environ['GIT_AUTHOR_NAME'] = u'{0} {1}'.format(request.user.first_name, request.user.last_name).encode('utf-8')
        os.environ['GIT_AUTHOR_EMAIL'] = request.user.email
        os.environ['USERNAME'] = str(request.user.username)

        w.repo.put_uploaded_file(git_path, doc)

        del(os.environ['GIT_AUTHOR_NAME'])
        del(os.environ['GIT_AUTHOR_EMAIL'])
        del(os.environ['USERNAME'])

        if format == "json":
            data = {
                'url': doc_path
            }

            return HttpResponse(json.dumps(data))

    return redirect(reverse('filemanager-index', args=[wiki, '']))