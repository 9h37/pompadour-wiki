# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.core.cache import cache
from django.utils.translation import ugettext
from django.utils.timezone import utc
from django.conf import settings

from pompadour_wiki.apps.utils.decorators import render_to, redirect_to
from pompadour_wiki.apps.utils import urljoin

from pompadour_wiki.apps.wiki.models import Wiki, WikiNotifier
from pompadour_wiki.apps.wiki.forms import EditPageForm

from pompadour_wiki.apps.lock.models import Lock
from pompadour_wiki.apps.filemanager.models import Attachment
from pompadour_wiki.apps.tagging.models import Tag

from pompadour_wiki.apps.markdown import pompadourlinks

import markdown
import datetime
import os

def notify(wiki):
    """ Send email notification after a commit. """

    if not settings.EMAIL_NOTIFY:
        return

    HEAD = wiki.repo.head.commit
    HEADp = wiki.repo.head.commit.parents[0]

    # Retrieve diff from cache
    key = u'diff_{0}_{1}'.format(HEADp.hexsha, HEAD.hexsha)

    if not cache.has_key(key):
        diff = wiki.repo.git.diff(HEADp.hexsha, HEAD.hexsha)

        cache.set(key, diff, cache.default_timeout)

    else:
        diff = cache.get(key)

    # Retrieve notifiers
    notifiers = [notifier.email for notifier in WikiNotifier.objects.filter(wiki=wiki)]

    # And send mail
    if notifiers:
        send_mail(u'[wiki/{0}] {1}'.format(wiki, HEAD.message), diff, os.environ['GIT_AUTHOR_EMAIL'], notifiers, fail_silently=True)

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

    # Retrieve content from cache
    key = request.get_full_path()

    if not cache.has_key(key):
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
        meta = md.Meta

        cache.set(key, (content, name, mimetype, meta), cache.default_timeout)

    else:
        content, name, mimetype, meta = cache.get(key)

    # Retrieve diff history from cache
    key = u'diffs_{0}'.format(request.get_full_path())

    if not cache.has_key(key):
        diffs = w.repo.get_file_diffs(real_path)

        cache.set(key, diffs, cache.default_timeout)

    else:
        diffs = cache.get(key)

    return {'wiki': {
        'name': os.path.splitext(name)[0],
        'path': path,
        'meta': meta,
        'content': content,
        'history': diffs,
        'obj': w,
        'tags': Tag.objects.filter(page=os.path.join(wiki, path)),
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
            os.environ['GIT_AUTHOR_EMAIL'] = request.user.email.encode('utf-8')
            os.environ['USERNAME'] = str(request.user.username)

            commit = form.cleaned_data['comment'].encode('utf-8') or None

            w.repo.set_content(new_fullpath, form.cleaned_data['content'], commit_msg=commit)

            notify(w)

            del(os.environ['GIT_AUTHOR_NAME'])
            del(os.environ['GIT_AUTHOR_EMAIL'])
            del(os.environ['USERNAME'])

            # Invalidate cache
            pageurl = reverse('view-page', args=[wiki, new_path])

            if cache.has_key(pageurl):
                cache.delete(pageurl)

            key = u'diffs_{0}'.format(pageurl)

            if cache.has_key(key):
                cache.delete(key)

            cache.delete('LastEdits')

            # And redirect user
            return {'REDIRECT': pageurl}

    # Edit
    else:
        if not w.repo.is_dir(path) and w.repo.exists(u'{0}.md'.format(path)):
            content, name, mimetype = w.repo.get_content(u'{0}.md'.format(path))
            form = EditPageForm({'path': path, 'content': content, 'comment': None})

        else:
            form = EditPageForm({'path': path})

    # Retrieve diff history from cache
    key = u'diffs_{0}'.format(reverse('view-page', args=[wiki, path]))

    if not cache.has_key(key):
        diffs = w.repo.get_file_diffs(path)

        cache.set(key, diffs, cache.default_timeout)

    else:
        diffs = cache.get(key)

    return {'wiki': {
        'name': os.path.splitext(name)[0],
        'path': path,
        'locked': locked,
        'lock': lock,
        'obj': w,
        'tags': Tag.objects.filter(page=os.path.join(wiki, path)),
        'history': diffs,
        'form': form,
        'attachments': Attachment.objects.filter(wiki=w, page=os.path.join(wiki, path)),
        'urls': {
            'remove': reverse('remove-page', args=[wiki, path]),
        },
    }}

@login_required
@redirect_to(lambda wiki, path: reverse('view-page', args=[wiki, path]))
def remove_page(request, wiki, path):
    w = get_object_or_404(Wiki, slug=wiki)

    # Remove page
    os.environ['GIT_AUTHOR_NAME'] = u'{0} {1}'.format(request.user.first_name, request.user.last_name).encode('utf-8')
    os.environ['GIT_AUTHOR_EMAIL'] = request.user.email.encode('utf-8')
    os.environ['USERNAME'] = str(request.user.username)

    w.repo.rm_content(u'{0}.md'.format(path))

    del(os.environ['GIT_AUTHOR_NAME'])
    del(os.environ['GIT_AUTHOR_EMAIL'])
    del(os.environ['USERNAME'])

    # Remove attachements
    Attachment.objects.filter(wiki=w, page=os.path.join(wiki, path)).delete()

    # Invalidate cache

    pageurl = reverse('view-page', args=[wiki, path])

    if cache.has_key(pageurl):
        cache.delete(pageurl)

    key = u'diffs_{0}'.format(pageurl)

    if cache.has_key(key):
        cache.delete(key)

    cache.delete('LastEdits')

    return wiki, ''
