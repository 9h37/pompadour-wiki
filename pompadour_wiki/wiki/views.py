from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from django.utils.timezone import utc

import datetime
import markdown
import os

from pompadour_wiki import pompadourlinks

from wiki.forms import EditPageForm
from wiki.models import Wiki, Document
from wiki.git_db import Repository

from lock.models import Lock

def _git_path(request, wiki):
    """ Get the path inside the git repository """

    path = request.path.split(u'/{0}/'.format(wiki))[1]

    # Remove slashes
    while path and path[0] == u'/':
        path = path[1:]

    while path and path[-1] == u'/':
        path = path[:-1]

    return path

@login_required
def tree(request, wiki):
    """ Return git tree """

    w = get_object_or_404(Wiki, slug=wiki)
    r = Repository(w.gitdir)
    return HttpResponse(r.get_json_tree())

@login_required
def diff(request, wiki):
    """ Return git diff """

    w = get_object_or_404(Wiki, slug=wiki)
    r = Repository(w.gitdir)
    return HttpResponse(r.get_history())

@login_required
def remove(request, wiki):
    """ Remove a page """

    w = get_object_or_404(Wiki, slug=wiki)
    r = Repository(w.gitdir)
    path = _git_path(request, wiki)

    # Remove page

    os.environ['GIT_AUTHOR_NAME'] = '{0} {1}'.format(request.user.first_name, request.user.last_name)
    os.environ['GIT_AUTHOR_EMAIL'] = request.user.email

    r.rm_content(path)

    del(os.environ['GIT_AUTHOR_NAME'])
    del(os.environ['GIT_AUTHOR_EMAIL'])

    # Remove attachements
    Document.objects.filter(wikipath=u'{0}/{1}'.format(wiki, path)).delete()

    return redirect(reverse(u'page', args=[wiki]))

@login_required
def edit(request, wiki):
    """ Edit a page """

    page_locked = False

    # Check if a lock exists
    try:
        lock = Lock.objects.get(path=request.path)

        # Check if the lock exists since more than 30 minutes
        dt = datetime.datetime.utcnow().replace(tzinfo=utc) - lock.timestamp

        if dt.total_seconds() >= 30*60:
            # The lock has expired
            # Reset it to the current user

            lock.user = request.user
            lock.timestamp = datetime.datetime.utcnow().replace(tzinfo=utc)
            lock.save()
        else:
            page_locked = True

    except Lock.DoesNotExist:
        lock = Lock()
        lock.path = request.path
        lock.user = request.user
        lock.timestamp = datetime.datetime.utcnow().replace(tzinfo=utc)
        lock.save()


    w = get_object_or_404(Wiki, slug=wiki)
    r = Repository(w.gitdir)
    path = _git_path(request, wiki)

    page_name = path

    if request.method == u'POST':
        form = EditPageForm(request.POST)

        if form.is_valid():
            new_path = '-'.join(form.cleaned_data[u'path'].split(' '))

            os.environ['GIT_AUTHOR_NAME'] = '{0} {1}'.format(request.user.first_name, request.user.last_name)
            os.environ['GIT_AUTHOR_EMAIL'] = request.user.email

            r.set_content(new_path, form.cleaned_data[u'content'])

            del(os.environ['GIT_AUTHOR_NAME'])
            del(os.environ['GIT_AUTHOR_EMAIL'])

            return redirect(u'{0}/{1}'.format(reverse(u'page', args=[wiki]), path))
    else:
        if r.exists(path) and not r.is_dir(path):
            content, page_name = r.get_content(path)
            form = EditPageForm({u'path': path, u'content': content})
        else:
            form = EditPageForm()

    docs = Document.objects.filter(wikipath=u'{0}/{1}'.format(wiki, path))

    data = {
        u'menu_url': reverse(u'tree', args=[wiki]),
        u'page_name': u'Edit: {0}'.format(page_name),
        u'page_locked': page_locked,
        u'attachements': {
            u'images': docs.filter(is_image=True),
            u'documents': docs.filter(is_image=False)
        },
        u'edit_path': path,
        u'wiki': w,
        u'form': form,
    }

    if page_locked:
        data[u'lock'] = lock

    return render_to_response(u'edit.html', data, context_instance=RequestContext(request))


@login_required
def page(request, wiki):
    w = get_object_or_404(Wiki, slug=wiki)
    r = Repository(w.gitdir)
    path = _git_path(request, wiki)

    # If the page doesn't exist, redirect user to an edit page
    if not r.exists(path):
        return redirect(u'{0}/{1}'.format(reverse('edit', args=[wiki]), path))

    if r.is_dir(path):
        pages, name = r.get_tree(path)
        data = {
            u'menu_url': reverse(u'tree', args=[wiki]),
            u'pages': pages,
            u'page_name': name,
            u'wiki': w,
        }

        return render_to_response(u'pages.html', data, context_instance=RequestContext(request))

    else:
        extension = pompadourlinks.makeExtension([
            (u'base_url', u'/wiki/{0}/'.format(wiki)),
            (u'end_url', u'.md'),
        ])

        md = markdown.Markdown(
            extensions = [u'meta', u'codehilite', u'toc', extension],
            safe_mode = True
        )
        content, name = r.get_content(path)

        page_content = md.convert(content.decode(u'utf-8'))

        docs = Document.objects.filter(wikipath=u'{0}/{1}'.format(wiki, path))

        data = {
            u'menu_url': reverse(u'tree', args=[wiki]),
            u'page_content': page_content,
            u'page_meta': md.Meta,
            u'page_name': name,
            u'attachements': {
                u'images': docs.filter(is_image=True),
                u'documents': docs.filter(is_image=False)
            },
            u'edit_url': u'/edit/'.join(request.path.split(u'/wiki/')),
            u'delete_url': u'/del/'.join(request.path.split(u'/wiki/')),
            u'wiki': w,
        }

        return render_to_response(u'page.html', data, context_instance=RequestContext(request))
