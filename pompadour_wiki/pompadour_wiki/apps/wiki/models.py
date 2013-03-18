# -*- coding: utf-8 -*-

from django.db import models

from pompadour_wiki.apps.utils.git_db import Repository

class Wiki(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField()
    gitdir = models.CharField(max_length=512)

    def __unicode__(self):
        return self.name

    @property
    def repo(self):
        return Repository(self.gitdir)

    def create_repo(self):
        """ Create repository """

        Repository.new(self.gitdir)

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
