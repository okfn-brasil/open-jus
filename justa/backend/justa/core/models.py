from django.db import models


class CourtOrder(models.Model):
    source = models.CharField(max_length=16)
    number = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    date = models.DateField()
    body = models.TextField(max_length=255, default='')
    text = models.TextField()

    class Meta:
        ordering = ('-date', 'name')
        unique_together = (("source", "number"),)
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['body']),
            models.Index(fields=['name']),
            models.Index(fields=['source', 'number']),
        ]
