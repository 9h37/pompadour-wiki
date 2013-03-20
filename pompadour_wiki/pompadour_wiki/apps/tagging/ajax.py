# -*- coding: utf-8 -*-

from django.template import Context, Template

from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax

from pompadour_wiki.apps.tagging.models import Tag

import os

TEMPLATE_TAG = """
<li id="tag_{{ tag.id }}">
    <a href="#">
        <i class="icon-tag"></i>
        {{ tag }}

        <i class="icon-remove" onclick="Dajaxice.pompadour_wiki.apps.tagging.del_tag(Dajax.process, {'tag': {{ tag.id }}});"></i>
    </a>
</li>
"""

@dajaxice_register
def add_tag(self, slug=None, path=None, tag=None):
    dajax = Dajax()

    if not slug or not path or not tag:
        return dajax.json()

    t = Tag()
    t.page = os.path.join(slug, path)
    t.tag = tag
    t.save()

    tmpl = Template(TEMPLATE_TAG)
    ctx = Context({'tag': t})

    dajax.append('#tags', 'innerHTML', tmpl.render(ctx))

    return dajax.json()

@dajaxice_register
def del_tag(self, tag=None):
    dajax = Dajax()

    if not tag:
        return dajax.json()

    try:
        t = Tag.objects.get(id=tag)

    except Tag.DoesNotExist:
        return dajax.json()

    dajax.remove('#tag_{0}'.format(t.id))

    t.delete()

    return dajax.json()