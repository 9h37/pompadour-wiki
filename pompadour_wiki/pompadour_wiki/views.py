# -*- coding: utf-8 -*-

from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify

from pompadour_wiki.apps.utils.decorators import render_to

from pompadour_wiki.apps.wiki.models import Wiki

from datetime import datetime
import os


class LastEdits(object):
    """
    This class is implemented as a list to make algorithm easier
    """

    def __init__(self, wikis):
        """ Get last edits """

        self.edits = []
        self.wikis = wikis

        for wiki in wikis:
            # Get the last ten commits
            last_10_commits = wiki.repo.log(limit=10)

            # And for each commits, add the modified files to the list
            for c in last_10_commits:
                if c.parents:
                    diff = c.tree.diff(c.parents[0].tree)

                    for patch in diff:
                        path = patch.new_file_path

                        # Exclude __media__ files :
                        if not path.startswith('__media__'):
                            node = {
                                'wiki': wiki,
                                'filename': path,
                                'page': os.path.splitext(path)[0],
                                'author': {
                                    'name': c.author.name,
                                    'email': c.author.email
                                },
                                'date': datetime.fromtimestamp(c.commit_time),
                            }

                            # Check if the file is in the list
                            if node not in self:
                                # Add the file to the list
                                self.edits.append(node)

                    # end for each diffs

                # No parents, root commit
                else:
                    # Add each files in the commit tree
                    for entry in wiki.repo.walk():
                        # Except __media__ files
                        if not entry.path.startswith('__media__'):
                            node = {
                                'wiki': wiki,
                                'filename': entry.path,
                                'page': os.path.splitext(entry.path)[0],
                                'author': {
                                    'name': c.author.name,
                                    'email': c.author.email
                                },
                                'date': datetime.fromtimestamp(c.commit_time),
                            }

                            # Check if the file is in the list
                            if node not in self:
                                # Add to the list
                                self.edits.append(node)

                    # end for each blob
            # end for each commits
        # end for each wikis

        self.edits.sort(key=lambda x: x['date'], reverse=True)

    # list API

    def __len__(self):
        return len(self.edits)

    def __getitem__(self, key):
        return self.edits[key]

    def __setitem__(self, key, value):
        self.edits[key] = value

    def __delitem__(self, key):
        del self.edits[key]

    def __iter__(self):
        return iter(self.edits)

    def __contains__(self, node):
        """ Check if the file is already in the list """

        for edit in self.edits:
            if edit['filename'] == node['filename'] and edit['wiki'] == node['wiki']:
                return True

        return False

@login_required
@render_to('index.html')
def home(request):
    wikis = Wiki.objects.all()

    # retrieve last edits from cache
    if not cache.has_key('LastEdits'):
        cache.set('LastEdits', LastEdits(wikis)[:10], cache.default_timeout)

    last_edits = cache.get('LastEdits')

    return {'wiki': {
        'home': True,
        'array': [wikis[x:x + 4] for x in range(0, len(wikis), 4)],
        'last_edits': last_edits,
    }}

@login_required
@render_to('index.html')
def search(request):
    wikis = Wiki.objects.all()

    # retrieve last edits from cache
    if not cache.has_key('LastEdits'):
        cache.set('LastEdits', LastEdits(wikis)[:10], cache.default_timeout)

    last_edits = cache.get('LastEdits')

    data = {'wiki': {
        'home': True,
        'array': [wikis[x:x + 4] for x in range(0, len(wikis), 4)],
        'last_edits': last_edits,
    }}

    if request.method == 'POST':
        query = request.POST['search-query']

        data['wiki']['search'] = query

        results = []

        # For each wiki
        for wiki in wikis:
            # Do the search
            for filename, matches in wiki.repo.search(query, exclude=r'^__media__'):
                # Get informations from the file
                print filename
                last_commit = wiki.repo.log(name=filename, limit=1)[0]

                # and append to the list
                results.append({
                    'id': '{0}_{1}'.format(last_commit.hex, slugify(filename)),
                    'wiki': wiki,
                    'file': os.path.splitext(filename)[0],
                    'matches': matches,
                    'author': last_commit.author,
                    'date': datetime.fromtimestamp(last_commit.commit_time),
                })

        # now sort the list
        results.sort(key=lambda x: x['date'], reverse=True)

        data['wiki']['search_results'] = results

    return data

@render_to('index.html')
def login_failed(request, message, status=None, template_name=None, exception=None):
    return {'error': message}