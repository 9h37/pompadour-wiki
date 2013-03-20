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
            last_10_commits = wiki.repo.get_history(limit=10)

            # And for each commits, add the modified files to the list
            for c in last_10_commits:
                if c.parents:
                    diffs = c.diff(c.parents[0])

                    for d in diffs:
                        # If a_blob is None, the file was deleted
                        # If b_blob is None, the file was added
                        # If none of them are None, the file was modified

                        blob = d.a_blob

                        # We don't want deleted files
                        if not blob:
                            continue

                        blob.path = self.sanitize_path(blob.path)


                        # Exclude __media__ files :
                        if not blob.path.startswith('__media__'):
                            node = {
                                'wiki': wiki,
                                'filename': blob.path,
                                'page': os.path.splitext(blob.path)[0],
                                'author': {
                                    'name': c.author.name,
                                    'email': c.author.email,
                                },
                                'date': datetime.fromtimestamp(c.authored_date),
                            }

                            # Check if the file is in the list
                            if node not in self:
                                # Add the file to the list
                                self.edits.append(node)

                    # end for each diffs

                # No parents, root commit
                else:
                    # Add each files in the commit tree
                    for blob in c.tree.traverse():
                        blob.path = self.sanitize_path(blob.path)

                        # Except __media__ files
                        if not blob.path.startswith('__media__'):
                            node = {
                                'wiki': wiki,
                                'filename': blob.path,
                                'page': os.path.splitext(blob.path)[0],
                                'author': {
                                    'name': c.author.name,
                                    'email': c.author.email,
                                },
                                'date': datetime.fromtimestamp(c.authored_date),
                            }

                            # Check if the file is in the list
                            if node not in self:
                                # Add to the list
                                self.edits.append(node)

                    # end for each blob
            # end for each commits
        # end for each wikis

        self.edits.sort(key=lambda x: x['date'], reverse=True)

    def sanitize_path(self, path):
        """
        If path[0] is ", then the path contains a UTF-8 string, why ?

        The output of git diff encode UTF-8 filenames :

            diff --git "a/H\303\251h\303\251.md" "b/H\303\251h\303\251.md"

        So, when GitPython read the diff output, it generate this path :

            "H\303\251h\303\251.md"

        And the path string (not unicode), contains :

            '"H\\303\\251h\\303\\251.md"'

        """

        if path[0] == '"':
            path = path[1:-1].decode('string-escape')

        return path.decode('utf-8')


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
        cache.set('last_edits', LastEdits(wikis)[:10], cache.default_timeout)

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
            for filename, matches in wiki.repo.search(query):
                # Get informations from the file
                last_commit = wiki.repo.get_file_history('{0}.md'.format(filename))[0]

                # and append to the list
                results.append({
                    'id': '{0}_{1}'.format(last_commit.hexsha, slugify(filename)),
                    'wiki': wiki,
                    'file': filename,
                    'matches': matches,
                    'author': {
                        'name': last_commit.author.name,
                        'email': last_commit.author.email
                    },
                    'date': datetime.fromtimestamp(last_commit.authored_date),
                })

        # now sort the list
        results.sort(key=lambda x: x['date'], reverse=True)

        data['wiki']['search_results'] = results

    return data

@render_to('index.html')
def login_failed(request, message, status=None, template_name=None, exception=None):
    return {'error': message}