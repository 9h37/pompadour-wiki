# -*- coding: utf-8 -*-

from django.db.models.signals import post_delete
from django.db import models

from django.utils.translation import ugettext
from django.core.cache import cache

from gitstorage.StorageBackend import GitStorage

class Wiki(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField()
    gitdir = models.CharField(max_length=512)

    def __unicode__(self):
        return self.name

    @property
    def repo(self):
        return GitStorage(self.gitdir)

    def create_repo(self):
        """ Create repository """

        GitStorage.create_storage(self.gitdir)


def invalidate_cache_on_delete(sender, **kwargs):
    """ When a Wiki is deleted, clear all cache """

    cache.clear()

    # Create empty commit
    wiki = kwargs.get('instance', None)

    if not wiki:
        raise AttributeError, 'instance is NoneType'

    # current user ???

    wiki.repo.commit(None, ugettext(u'Wiki deleted'))

post_delete.connect(invalidate_cache_on_delete, sender=Wiki)

class WikiNotifier(models.Model):
    wiki = models.ForeignKey(Wiki)
    email = models.EmailField(max_length=254)

    def __unicode__(self):
        return self.email

class Document(models.Model):
    path = models.CharField(max_length=512)
    wikipath = models.CharField(max_length=512)
    is_image = models.BooleanField()

    def __unicode__(self):
        return self.path
