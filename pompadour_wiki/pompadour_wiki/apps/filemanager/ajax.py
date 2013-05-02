# -*- coding: utf-8 -*-

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from django.template.loader import get_template
from django.template import Context

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext

from pompadour_wiki.apps.filemanager.models import Attachment
from pompadour_wiki.apps.wiki.models import Wiki
from pompadour_wiki.apps.utils import urljoin, decode_unicode_references

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
   
    for f in files:
        path = os.path.join('__media__', *f.split('/'))

        w.repo.delete(path)
        w.repo.commit(request.user, ugettext(u'Update Wiki: {0} deleted'.format(path)).encode('utf-8'))

        # Remove attachments
        Attachment.objects.filter(file=f).delete()


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

    page = decode_unicode_references(page)

    for f in files:
        urlpage = urljoin(wiki, page.encode('utf-8'))

        # check if the attachment already exist
        if not Attachment.objects.filter(wiki=w, page=urlpage, file=f):
            # the attachment doesn't exist, we can add it
            a = Attachment()
            a.wiki = w
            a.page = urlpage
            a.file = f
            a.mimetype = w.repo.mimetype(os.path.join('__media__', *f.split('/')))

            a.save()

            tmpl = get_template('wiki/attachitem.html')
            rendered = tmpl.render(Context({
                'wiki': {
                    'obj': w,
                },
                'doc': a,
            }))

            dajax.add_data(rendered, 'append_attached_document')
            dajax.alert(ugettext(u'{0} attached to {1}').format(f, page))

    return dajax.json()

@dajaxice_register
def remove_attach(request, attachment=None):
    dajax = Dajax()

    if not attachment:
        return dajax.json()

    Attachment.objects.filter(pk=attachment).delete()

    dajax.script('window.location.reload();')

    return dajax.json()