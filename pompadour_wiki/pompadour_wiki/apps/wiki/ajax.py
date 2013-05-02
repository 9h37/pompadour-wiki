# -*- coding: utf-8 -*-

from django.template.defaultfilters import slugify
from django.template.loader import render_to_string, get_template
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.utils.translation import ugettext
from django.conf import settings

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from pompadour_wiki.apps.wiki.models import Wiki
from pompadour_wiki.apps.markdown import pompadourlinks

from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter
import markdown

import os

@dajaxice_register
def add_wiki(request, dform=None):
    dajax = Dajax()

    if not dform:
        return dajax.json()

    wiki = Wiki()
    wiki.name = dform['add-wiki-name'].encode('utf-8')
    wiki.slug = slugify(wiki.name)
    wiki.description = dform['add-wiki-desc'].encode('utf-8')
    wiki.gitdir = os.path.join(settings.WIKI_GIT_DIR, wiki.slug)

    try:
        w = Wiki.objects.get(slug=wiki.slug)

        dajax.assign('#error', 'innerHTML',
                    render_to_string('error.html',
                                     {'error': ugettext(u'Can\'t add wiki, another wiki with the same name ({0}) already exists.').format(wiki.name)},
                                     context_instance=RequestContext(request)
                    )
        )

    except Wiki.DoesNotExist:
        wiki.create_repo(request.user)
        wiki.save()

        dajax.redirect(reverse('view-page', args=[wiki.slug, '']))

    return dajax.json()


@dajaxice_register
def edit_preview(request, dform=None, wiki=None):
    dajax = Dajax()

    if not dform or not wiki:
        return dajax.json()

    content = dform['content']

    # Generate markdown document
    extension = pompadourlinks.makeExtension([
        ('base_url', u'/wiki/{0}/'.format(wiki)),
        ('end_url', ''),
    ])

    md = markdown.Markdown(
        extensions = ['meta', 'codehilite', 'toc', extension],
        safe_mode = True
    )

    content = md.convert(content)
    dajax.assign('#edit-preview', 'innerHTML', content)

    return dajax.json()

@dajaxice_register
def show_diff(request, sha=None, parent_sha=None, wiki=None, path=None):
    dajax = Dajax()

    if not sha or not parent_sha or not wiki:
        return dajax.json()

    # Retrieve git repository
    try:
        w = Wiki.objects.get(slug=wiki)

    except Wiki.DoesNotExist:
        return dajax.json()

    def get_diff_from_cache(wiki, sha, parent_sha, path):
        """ Retrieve diff from cache """

        key = u'diff_{0}_{1}'.format(sha, parent_sha)

        if path:
            key = u'{0}_{1}'.format(key, path)

        if not cache.has_key(key):
            # Retrieve real diff
            if path:
                diff = w.repo.diff(parent_sha, sha, path)

            else:
                diff = w.repo.diff(parent_sha, sha)

            cache.set(key, diff, cache.default_timeout)

        return cache.get(key)

    diff = get_diff_from_cache(w, sha, parent_sha, path)

    dajax.assign('#diff', 'innerHTML', highlight(diff, DiffLexer(), HtmlFormatter(cssclass='codehilite')))

    return dajax.json()
