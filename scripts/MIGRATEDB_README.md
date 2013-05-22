Be sure to have the virtualenv activated before doing anything else !

Migrate Git database :

    (virtualenv) $ python migrategitdb.py path/to/git/repo path/to/other/git/repo

Migrate metadata stored in SQL database :

    (virtualenv) $ ../pompadour_wiki/manage.py shell
    >>> import sys, os
    >>> sys.path.append(os.getcwd())
    >>> import migrategitdb
    >>> migrategitdb.django_migrate()
