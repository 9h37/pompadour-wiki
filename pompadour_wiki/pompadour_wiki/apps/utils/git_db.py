# -*- coding: utf-8 -*-

from django.utils.translation import ugettext
from django.utils import simplejson as json
from django.conf import settings

from StringIO import StringIO
from gitdb import IStream
from git import *
from git.exc import InvalidGitRepositoryError

from collections import defaultdict
from datetime import datetime
import os


_hook = """#!/bin/sh
cd ..
env -i git reset --hard > /dev/null 2>&1
env -i git update-index > /dev/null 2>&1
"""

def _do_commit(repo, path, content, commit_msg=None):
    """ Do a commit """

    # Create the blob object
    stream = StringIO(content.encode('utf-8'))
    stream.seek(0, 2)
    streamlen = stream.tell()
    stream.seek(0)

    istream = IStream('blob', streamlen, stream)

    # Add it to the repository object database
    repo.odb.store(istream)

    # Create the corresponding Blob object
    blob = Blob(repo, istream.binsha, Blob.file_mode, path.encode('utf-8'))

    # Add blob to the index
    repo.index.add([IndexEntry.from_blob(blob)])

    if not commit_msg:
        commit_msg = ugettext(u'Update Wiki: {0}').format(path).encode('utf-8')

    repo.index.commit(commit_msg)


class Repository(object):
    """ Repository object. """

    @classmethod
    def new(cls, gitdir):
        """ Initialize a repository and create the root commit """

        # Create repository
        if os.path.exists(gitdir.encode('utf-8')):
            return cls(gitdir)

        repo = Repo.init(gitdir.encode('utf-8'))
        repo.config_writer().set_value('receive', 'denyCurrentBranch', 'ignore')

        # Create hook to automatically update when we receive commits from clients

        post_receive = os.path.join(gitdir, '.git', 'hooks', 'post-receive')

        with open(post_receive, 'w') as f:
            f.write(_hook)
        
        os.chmod(post_receive, 0775)

        # Create the initial commit
        _do_commit(repo, u'{0}.md'.format(settings.WIKI_INDEX), '# Home', commit_msg=ugettext(u'Initialize'))

        return cls(gitdir)

    def __init__(self, gitdir):
        """ Initialize repository. """

        self.repo = Repo(gitdir.encode('utf-8'))
        self.gitdir = gitdir
        self.parse()

    @property
    def git(self):
        return self.repo.git

    @property
    def head(self):
        return self.repo.head

    def parse(self):
        """ Parse Tree and Blob objects. """

        # Do git reset --hard and git update-index
        self.repo.head.reset(index=True, working_tree=True)
        self.repo.git.update_index()

        self.repo_tree = self.repo.tree()
        self.entries = [e for e in self.repo_tree.traverse()]
        self.blobs = [b for b in self.entries if isinstance(b, Blob)]
        self.trees = [self.repo_tree] + [t for t in self.entries if isinstance(t, Tree)]

    def exists(self, path):
        """ Check if path exists in repository. """

        if path == self.repo_tree.path:
            return True

        for e in self.entries:
            if path == e.path:
                return True

        return False

    def is_dir(self, path):
        """ Check if path is a directory. """

        for t in self.trees:
            if path == t.path:
                return True

        return False

    def get_file_mimetype(self, path):
        """ Get mimetype of file stored in ``path``. """

        if self.is_dir(path):
            return 'inode/directory'
            
        for blob in self.blobs:
            if blob.path == path:
                return blob.mime_type

    def set_content(self, path, content, commit_msg=None):
        """ Add new content in ``path``. """

        _do_commit(self.repo, path, content, commit_msg)

        # Update internal informations
        self.parse()

    def put_uploaded_file(self, path, ufile, commit_msg=None):
        """ Put an uploaded file to the repository. """

        # Re-parse to be sure
        self.parse()

        # Get absolute path to the file
        abspath = os.path.join(self.gitdir, path)

        # Make directory for the file
        try:
            os.makedirs(os.path.dirname(abspath))
        except OSError:
            pass

        # Write the file
        with open(abspath, 'wb') as f:
            for chunk in ufile.chunks():
                f.write(chunk)

        # Add it to the repository
        self.repo.index.add([path.encode('utf-8')])

        # And commit
        if not commit_msg:
            commit_msg = ugettext(u'Upload document: {0}').format(path).encode('utf-8')

        self.repo.index.commit(commit_msg)

        # Update internal informations
        self.parse()

    def get_content(self, path):
        """ Get content of file stored in ``path``. """

        for blob in self.blobs:
            if blob.path == path:
                return blob.data_stream.read(), blob.name, blob.mime_type

    def rm_content(self, path):
        """ Remove file located at ``path``. """

        self.repo.index.remove([path.encode('utf-8')])
        self.repo.index.commit(ugettext(u'Update Wiki: {0} deleted'.format(path)).encode('utf-8'))

        self.parse()

    def commit(self, message):
        """ Create an empty commit """

        c = Commit.create_from_tree(self.repo, self.repo.tree(), message, head=True)

    def get_folder_tree(self, path):
        """ Get list of files contained in ``path``. """

        for tree in self.trees:
            if tree.path == path:
                ret = []

                ret = ret + [{'path': b.path, 'name': b.name, 'type': b.mime_type} for b in tree.blobs]
                ret = ret + [{'path': t.path, 'name': t.name, 'type': 'inode/directory'} for t in tree.trees]

                return ret

    def get_file_history(self, path):
        """ Get history for a file """
        return [self.repo.commit(line.split(' ', 1)[0]) for line in self.repo.git.log('--pretty=oneline', '--', path.encode('utf-8')).splitlines()]

    def get_history(self, limit=None):
        """ Get repository's history """

        if limit:
            return [self.repo.commit(line.split(' ', 1)[0]) for line in self.repo.git.log('--pretty=oneline', '-{0}'.format(limit)).splitlines()]

        return [self.repo.commit(line.split(' ', 1)[0]) for line in self.repo.git.log('--pretty=oneline').splitlines()]

    def get_file_diffs(self, path):
        """ Get diffs for a file """

        diffs = {'diffs': []}

        if self.exists(path):
            commits = self.get_file_history(path)

            for c in commits:
                diff = {
                    'msg': c.message,
                    'date': datetime.fromtimestamp(c.authored_date),
                    'author': c.author.name,
                    'sha': c.hexsha,
                    'path': path,
                }

                if c.parents:
                    diff['parent_sha'] = c.parents[0].hexsha

                diffs['diffs'].append(diff)

        return diffs

    def get_diffs(self, limit=None):
        """ Return repository's diffs. """

        commits = self.get_history(limit=limit)

        diffs = {'diffs': []}

        for c in commits:
            diff = {
                'msg': c.message,
                'date': datetime.fromtimestamp(c.authored_date),
                'author': c.author.name,
                'sha': c.hexsha
            }

            if c.parents:
                diff['parent_sha'] = c.parents[0].hexsha

            diffs['diffs'].append(diff)

        return diffs

    def get_tree(self):
        """ Get full tree of repository as json. """

        ret = {'node': {
            'name': '/',
            'path': '/',
            'type': 'tree',
            'children': []
        }}

        # Get all paths from the repository
        for e in self.entries:
            spath = e.path.split('/')

            # We do not want the __media__ in our tree
            if spath[0] == '__media__':
                continue

            node = ret['node']

            # Build tree before inserting node
            for d in spath[:-1]:
                new_node = {'node': {
                    'name': d,
                    'path': e.path,
                    'type': 'tree',
                    'children': []
                }}

                # Search if the node is already in the tree
                for n in node['children']:
                    if d == n['node']['name']:
                        new_node = n
                        break

                # If not, just add it
                else:
                    node['children'].append(new_node)

                # Up level
                node = new_node['node']

            if isinstance(e, Tree):
                new_node = {'node': {
                    'name': e.name,
                    'path': e.path,
                    'type': 'tree',
                    'children': []
                }}

            else:
                new_node = {'node': {
                    'name': e.name,
                    'path': e.path,
                    'type': 'file'
                }}

            node['children'].append(new_node)

        return ret

    def get_json_tree(self):
        return json.dumps(self.get_tree())

    def search(self, pattern):
        """ Search for a pattern inside the repository and returns the list of results. """

        results = []

        # Do the search
        try:
            out = self.git.grep('-i', '-I', '--cached', pattern.encode('utf-8'))

        except GitCommandError:
            # No results found
            return []

        for line in out.splitlines():
            # Exclude __media__
            if not line.startswith('__media__'):
                sep = line.find(':')

                url = line[:sep]
                match = line[sep + 1:]

                # Remove markdown extension
                if url.endswith('.md'):
                    url = url[:url.rfind('.md')]

                # Append to the results
                results.append ((url, match))

        # Group results
        groups = defaultdict(list)

        for result in results:
            groups[result[0]].append(result[1])

        results = groups.items()

        return results
