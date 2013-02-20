# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify

from pompadour_wiki.apps.utils.decorators import render_to

from pompadour_wiki.apps.wiki.models import Wiki

from datetime import datetime

@login_required
@render_to('index.html')
def home(request):
    wikis = Wiki.objects.all()

    last_edits = []

    # For each wiki
    for wiki in wikis:
        last_10_commits = wiki.repo.get_history(limit=10)

        for commit in last_10_commits:
            last_edits.append({
                'id': commit.hexsha,
                'wiki': wiki,
                'message': commit.message,
                'author': commit.author,
                'date': datetime.fromtimestamp(commit.authored_date),
            })

    last_edits.sort(key=lambda x: x['date'], reverse=True)

    return {'wiki': {
        'home': True,
        'array': [wikis[x:x + 4] for x in range(0, len(wikis), 4)],
        'last_edits': last_edits[:10]
    }}

@login_required
@render_to('index.html')
def search(request):
    wikis = Wiki.objects.all()

    last_edits = []

    # For each wiki
    for wiki in wikis:
        last_10_commits = wiki.repo.get_history(limit=10)

        for commit in last_10_commits:
            last_edits.append({
                'id': commit.hexsha,
                'wiki': wiki,
                'message': commit.message,
                'author': commit.author,
                'date': datetime.fromtimestamp(commit.authored_date),
            })

    last_edits.sort(key=lambda x: x['date'], reverse=True)

    data = {'wiki': {
        'home': True,
        'array': [wikis[x:x + 4] for x in range(0, len(wikis), 4)],
        'last_edits': last_edits[:10]
    }}

    if request.method == 'POST':
        query = request.POST['search-query']

        data['wiki']['search'] = query

        results = []

        # For each wiki
        for wiki in wikis:
            # Do the search
            for filename, matches in wiki.repo.search(query):
                print '\033[01mDEBUG:', wiki, filename, '\033[00m'

                # Get informations from the file
                last_commit = wiki.repo.get_file_history(u'{0}.md'.format(filename.decode('utf-8')).encode('utf-8'))[0]

                # and append to the list
                results.append({
                    'id': '{0}_{1}'.format(last_commit.hexsha, slugify(filename)),
                    'wiki': wiki,
                    'file': filename,
                    'matches': matches,
                    'author': last_commit.author,
                    'date': datetime.fromtimestamp(last_commit.authored_date),
                })

        # now sort the list
        results.sort(key=lambda x: x['date'], reverse=True)

        data['wiki']['search_results'] = results

    return data



@render_to('index.html')
def login_failed(request, message, status=None, template_name=None, exception=None):
    return {'error': message}