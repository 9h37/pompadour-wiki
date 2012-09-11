from django.db import models

class Wiki(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    description = models.TextField()
    gitdir = models.CharField(max_length=512)

    def __unicode__(self):
        return self.name

class Document(models.Model):
    path = models.CharField(max_length=512)
    wikipath = models.CharField(max_length=512)
    is_image = models.BooleanField()

    def __unicode__(self):
        return self.path

