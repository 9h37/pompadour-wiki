from django.db import models
from django.contrib.auth.models import User

class Lock(models.Model):
    path = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.path
