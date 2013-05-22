#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import subprocess
import os

def stripspecialchars(input_str):
    """ Remove special chars in UTF-8 string """

    import unicodedata

    nfkd_form = unicodedata.normalize('NFKD', unicode(input_str))

    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

class MigrateException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class MigrateDB(object):
    def __init__(self, path):
        if not os.path.exists(path):
            raise MigrateException(path + ": Not found")

        if not os.path.isdir(path):
            raise MigrateException(path + ": Not a directory")

        self.path = path

    def __call__(self):
        files = []

        # get files
        for (dirpath, dirnames, filenames) in os.walk(self.path):            
            for filename in filenames:
                if '.git' not in dirpath.split(os.sep):
                    files.append(os.sep.join([dirpath, filename]).decode('utf-8'))

        # rename files
        newfiles = []

        for filename in files:            
            newfilepath = stripspecialchars(filename)

            print "---- Moving", filename, "to", newfilepath
            
            newdirpath = os.path.dirname(newfilepath)

            if not os.path.exists(newdirpath):
                os.makedirs(newdirpath)

            os.rename(filename, newfilepath)

            newfiles.append(newfilepath[len(self.path) + 1:])

        # commit it

        subprocess.call(["git", "add"] + newfiles, cwd=self.path)
        subprocess.call(["git", "commit", "-m", "Migrate Database"], cwd=self.path)

    @classmethod
    def django_migrate(cls):
        from pompadour_wiki.apps.filemanager.models import Attachment
        from pompadour_wiki.apps.tagging.models import Tag

        for a in Attachment.objects.all():
            a.page = stripspecialchars(a.page)
            a.save()

        for t in Tag.objects.all():
            t.page = stripspecialchars(t.page)
            t.save()



if __name__ == "__main__":
    import sys

    try:
        for dirname in sys.argv[1:]:
            print "-- Migrating:", dirname

            mdb = MigrateDB(dirname)
            mdb()

            print "-- Migration done:", dirname

    except MigrateException, e:
        print >>sys.stderr, e