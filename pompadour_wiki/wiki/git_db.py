from django.utils.translation import ugettext

from StringIO import StringIO
from gitdb import IStream
from git import *
from git.exc import InvalidGitRepositoryError
import simplejson

class Repository(object):
    """ Repository object """

    def __init__(self, gitdir):
        """ Initialize repository """

        try:
            self.repo = Repo(gitdir)
        except InvalidGitRepositoryError:
            pass

        self._parse()

    def _parse(self):
        self.repo_tree = self.repo.head.commit.tree
        self.blobs = []
        self.trees = [self.repo_tree]

        for e in self.repo_tree.traverse():
            if type(e) is Tree:
                self.trees.append(e)
            else:
                self.blobs.append(e)

    def exists(self, path):
        """ Check if path exists in repository """

        if path == self.repo_tree.path:
            return True

        for e in self.repo_tree.traverse():
            if e.path == path:
                return True

        return False

    def is_dir(self, path):
        """ Check if path is a directory """

        if path == self.repo_tree.path:
            return True

        for e in self.repo_tree.traverse():
            if e.path == path and type(e) is Tree:
                return True

        return False

    def set_content(self, path, content):
        """ Add new content in `path` """

        # Create the stream
        stream = StringIO(content.encode('utf-8'))
        stream.seek(0, 2)
        streamlen = stream.tell()
        stream.seek(0)

        istream = IStream("blob", streamlen, stream)

        # Add it to the repository object database
        self.repo.odb.store(istream)

        # Create the corresponding blob object
        blob = Blob(self.repo, istream.binsha, 0100644, path.encode('utf-8'))

        # Commit
        self.repo.index.add([IndexEntry.from_blob(blob)])
        self.repo.index.commit(ugettext('Update Wiki: {0}').format(path.encode('utf-8')).encode('utf-8'))

        # Update internal informations
        self._parse()

    def get_content(self, path):
        """ Get content of file stored in `path` """
        for blob in self.blobs:
            if blob.path == path:
                return blob.data_stream.read(), blob.name

    def rm_content(self, path):
        """ Remove file located at `path` """

        self.repo.index.remove([path])
        self.repo.index.commit(ugettext('Update Wiki: {0} deleted').format(path.encode('utf-8')).encode('utf-8'))

        # Updata internal informations
        self._parse()

    def get_tree(self, path):
        """ Get list of files contained in `path` """

        for tree in self.trees:
            if tree.path == path:
                ret = []

                ret = ret + [{u'path': b.path, u'type': u'file'} for b in tree.blobs]
                ret = ret + [{u'path': t.path, u'type': u'tree'} for t in tree.trees]

                return ret, tree.name

    def get_json_tree(self):
        """ Get full tree of repository as json """

        json = {u'node': {
            u'name': u'/',
            u'path': u'/',
            u'type': u'tree',
            u'children': []
        }}

        # Get all paths from the repository
        for e in self.repo_tree.traverse():
            spath = e.path.split(u'/')

            node = json[u'node']

            # Build tree before inserting node
            for d in spath[:-1]:
                new_node = {u'node': {
                    u'name': d,
                    u'path': e.path,
                    u'type': u'tree',
                    u'children': []
                }}

                # Search if the node is already in the tree
                for n in node[u'children']:
                    if d == n[u'node'][u'name']:
                        new_node = n
                        break
                else: # if not, just add it
                    node[u'children'].append(new_node)

                # Up level
                node = new_node[u'node']

            if type(e) is Tree:
                new_node = {u'node': {
                    u'name': e.name,
                    u'path': e.path,
                    u'type': u'tree',
                    u'children': []
                }}

                node[u'children'].append(new_node)
            else:
                new_node = {u'node': {
                    u'name': e.name,
                    u'path': e.path,
                    u'type': u'file'
                }}

                node[u'children'].append(new_node)

        return simplejson.dumps(json)

    def get_history(self):
        diffs = {u'diffs': []}

        c = self.repo.head.commit

        while c.parents:
            diff = {u'msg': unicode(c.message), u'date': unicode(c.authored_date), u'author': unicode(c.author)}
            diff[u'diff'] = self.repo.git.diff(c.parents[0].hexsha, c.hexsha)

            diffs[u'diffs'].append(diff)

            c = c.parents[0]

        return simplejson.dumps(diffs)
