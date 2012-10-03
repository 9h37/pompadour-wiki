from django.core.urlresolvers import reverse
from django.conf import settings

from wiki.models import Wiki

def _infos():
    infos = {
        u'title': u'Pompadour Wiki'
    }

    return infos

def _navbar():
    urls = {u'navbar': [
        'separator'
    ]}

    for w in Wiki.objects.all():
        entry = (w.name, u'/wiki/{0}/'.format(w.slug), None)

        urls[u'navbar'].append(entry)

    return urls

def pompadour(request):
    data = {u'pompadour': {}}

    data[u'pompadour'].update(_infos())
    data[u'pompadour'].update(_navbar())

    return data
