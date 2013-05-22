Be sure to have the virtualenv activated before doing anything else !

Migrate Git database :

    (virtualenv) $ python migrategitdb.py <list of paths to your repositories>

Migrate metadata stored in SQL database :

    (virtualenv) $ ../pompadour_wiki/manage.py shell
    >>> import sys, os
    >>> sys.path.append(os.getcwd())
    >>> import migrategitdb
    >>> migrategitdb.MigrateDB.django_migrate()
