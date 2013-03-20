from django.db import models

class Tag(models.Model):
    page = models.CharField(max_length=512)
    tag = models.CharField(max_length=75)

    class Meta:
        unique_together = (
            ('page', 'tag'),
        )