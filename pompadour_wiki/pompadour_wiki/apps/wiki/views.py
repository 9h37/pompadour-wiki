# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext
from django.utils.timezone import utc
from django.conf import settings

from pompadour_wiki.apps.utils.decorators import render_to, redirect_to
from pompadour_wiki.apps.utils import urljoin

from pompadour_wiki.apps.wiki.models import Wiki
from pompadour_wiki.apps.wiki.forms import EditPageForm

from pompadour_wiki.apps.lock.models import Lock
from pompadour_wiki.apps.filemanager.models import Attachment

from pompadour_wiki.apps.markdown import pompadourlinks

import markdown
import datetime
import os

@login_required
@render_to('wiki/view.html')
def view_page(request, wiki, path):
    w = get_object_or_404(Wiki, slug=wiki)

    if not path:
        return {'REDIRECT': urljoin(request.path, settings.WIKI_INDEX)}

    # If path is a folder
    if w.repo.is_dir(path):
        if settings.WIKI_INDEX:
            return {'REDIRECT': urljoin(request.path, settings.WIKI_INDEX)}

        pages, name = r.get_tree(path)
        return {'wiki': {
            'name': name,
            'pages': pages,
            'obj': w
        }}

    real_path = u'{0}.md'.format(path)

    # If the page doesn't exist, redirect user to an edit page
    if not w.repo.exists(real_path):
        return {'REDIRECT': reverse('edit-page', args=[wiki, path])}

    # Generate markdown document
    extension = pompadourlinks.makeExtension([
        ('base_url', u'/wiki/{0}/'.format(wiki)),
        ('end_url', ''),
    ])

    md = markdown.Markdown(
        extensions = ['meta', 'codehilite', 'toc', extension],
        safe_mode = True
    )

    content, name, mimetype = w.repo.get_content(real_path)
    content = md.convert(content.decode('utf-8'))

    return {'wiki': {
        'name': os.path.splitext(name)[0],
        'path': path,
        'meta': md.Meta,
        'content': content,
        'history': w.repo.get_file_diffs(real_path),
        'obj': w,
        'attachments': Attachment.objects.filter(wiki=w, page=os.path.join(wiki, path)),
        'urls': {
            'edit': os.path.join(request.path, 'edit'),
            'remove': os.path.join(request.path, 'remove'),
        },
    }}

@login_required
@render_to('wiki/edit.html')
def edit_page(request, wiki, path):
    locked = False

    # check if a lock exists
    try:
        lock = Lock.objects.get(path=request.path)

        if lock.user != request.user:
            # check if the lock exists since more than 30 minutes
            dt = datetime.datetime.utcnow().replace(tzinfo=utc) - lock.timestamp

            if dt.total_seconds() >= 30*60:
                # The lock has expired
                # Reset it to the current user

                lock.user = request.user
                lock.timestamp = datetime.datetime.utcnow().replace(tzinfo=utc)
                lock.save()
            else:
                locked = True

    except Lock.DoesNotExist:
        lock = Lock()
        lock.path = request.path
        lock.user = request.user
        lock.timestamp = datetime.datetime.utcnow().replace(tzinfo=utc)
        lock.save()

    w = get_object_or_404(Wiki, slug=wiki)
    name = ''

    # Save
    if request.method == 'POST':
        form = EditPageForm(request.POST)

        if form.is_valid():
            new_path = u'-'.join(form.cleaned_data['path'].split(u' '))
            new_fullpath = u'{0}.md'.format(new_path)

            os.environ['GIT_AUTHOR_NAME'] = u'{0} {1}'.format(request.user.first_name, request.user.last_name).encode('utf-8')
            os.environ['GIT_AUTHOR_EMAIL'] = request.user.email
            os.environ['USERNAME'] = str(request.user.username)

            commit = form.cleaned_data['comment'].encode('utf-8') or None

            w.repo.set_content(new_fullpath, form.cleaned_data['content'], commit_msg=commit)

            del(os.environ['GIT_AUTHOR_NAME'])
            del(os.environ['GIT_AUTHOR_EMAIL'])
            del(os.environ['USERNAME'])

            return {'REDIRECT': reverse('view-page', args=[wiki, new_path])}

    # Edit
    else:
        if not w.repo.is_dir(path) and w.repo.exists(u'{0}.md'.format(path)):
            content, name, mimetype = w.repo.get_content(u'{0}.md'.format(path))
            form = EditPageForm({'path': path, 'content': content, 'comment': None})

        else:
            form = EditPageForm({'path': path})

    return {'wiki': {
        'name': os.path.splitext(name)[0],
        'path': path,
        'locked': locked,
        'lock': lock,
        'obj': w,
        'history': w.repo.get_file_diffs(path),
        'form': form,
        'attachments': Attachment.objects.filter(wiki=w, page=os.path.join(wiki, path)),
    }}

@login_required
@redirect_to(lambda wiki, path: reverse('view-page', args=[wiki, path]))
def remove_page(request, wiki, path):
    w = get_object_or_404(Wiki, slug=wiki)

    # Remove page
    os.environ['GIT_AUTHOR_NAME'] = u'{0} {1}'.format(request.user.first_name, request.user.last_name).encode('utf-8')
    os.environ['GIT_AUTHOR_EMAIL'] = request.user.email
    os.environ['USERNAME'] = str(request.user.username)

    w.repo.rm_content(u'{0}.md'.format(path))

    del(os.environ['GIT_AUTHOR_NAME'])
    del(os.environ['GIT_AUTHOR_EMAIL'])
    del(os.environ['USERNAME'])

    # Remove attachements
    Attachment.objects.filter(wiki=w, page=os.path.join(wiki, path)).delete()

    return wiki, ''
