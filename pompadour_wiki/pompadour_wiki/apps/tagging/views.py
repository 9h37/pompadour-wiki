# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required

from pompadour_wiki.apps.utils.decorators import render_to
from pompadour_wiki.apps.tagging.models import Tag
from pompadour_wiki.apps.wiki.models import Wiki

@login_required
@render_to('tagging/view.html')
def view_tag(request, tagname):
    tags = Tag.objects.filter(tag=tagname)

    data = {'wiki': {
        'home': True,
        'tagname': tagname,
        'tags': [],
    }}

    for tag in tags:
        wiki_slug, path = tag.page.split('/', 1)

        try:
            wiki = Wiki.objects.get(slug=wiki_slug)

        except Wiki.DoesNotExist:
            continue

        data['wiki']['tags'].append({
            'wiki': wiki,
            'path': path
        })

    return data