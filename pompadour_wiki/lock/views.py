from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from lock.models import Lock

import simplejson as json


@login_required
def detail(request, lock_id):
    lock = get_object_or_404(Lock, pk=lock_id)

    data = {u'lock': {
        u'id': lock.id,
        u'path': lock.path,
        u'user': lock.user.username
    }}

    if request.method == u'DELETE' and request.user == lock.user:
        lock.delete()
        data[u'lock'][u'deleted'] = True

    return HttpResponse(json.dumps(data))
