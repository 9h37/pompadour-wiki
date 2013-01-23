# -*- coding: utf-8 -*-

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from django.core.urlresolvers import reverse

from pompadour_wiki.apps.filemanager.models import Attachment
from pompadour_wiki.apps.wiki.models import Wiki
from pompadour_wiki.apps.utils.git_db import Repository
from pompadour_wiki.apps.utils import urljoin

import os

@dajaxice_register
def remove_doc(request, wiki=None, files=None):
    dajax = Dajax()

    if not wiki or not files:
        return dajax.json()

    try:
        w = Wiki.objects.get(slug=wiki)
    except Wiki.DoesNotExist:
        return dajax.json()

    r = Repository(w.gitdir)
        
    os.environ['GIT_AUTHOR_NAME'] = u'{0} {1}'.format(request.user.first_name, request.user.last_name).encode('utf-8')
    os.environ['GIT_AUTHOR_EMAIL'] = request.user.email
    os.environ['USERNAME'] = str(request.user.username)

    for f in files:
        path = os.path.join('__media__', *f.split('/'))

        r.rm_content(path)

        # Remove attachments
        Attachment.objects.filter(file=f).delete()

    del(os.environ['GIT_AUTHOR_NAME'])
    del(os.environ['GIT_AUTHOR_EMAIL'])
    del(os.environ['USERNAME'])

    dajax.redirect(reverse('filemanager-index', args=[wiki, '']))

    return dajax.json()

@dajaxice_register
def attach_doc(request, wiki=None, files=None, page=None):
    dajax = Dajax()

    if not wiki or not files or not page:
        return dajax.json()

    try:
        w = Wiki.objects.get(slug=wiki)
    except Wiki.DoesNotExist:
        return dajax.json()

    r = Repository(w.gitdir)

    for f in files:
        a = Attachment()
        a.wiki = w
        a.page = urljoin(wiki, page)
        a.file = f
        a.mimetype = r.get_file_mimetype(os.path.join('__media__', *f.split('/')))

        a.save()

    return dajax.json()

@dajaxice_register
def remove_attach(request, attachment=None):
    dajax = Dajax()

    if not attachment:
        return dajax.json()

    Attachment.objects.filter(pk=attachment).delete()

    dajax.script('window.location.reload();')

    return dajax.json()