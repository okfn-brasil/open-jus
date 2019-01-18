from django.db import models


class CourtOrder(models.Model):
    source = models.CharField(max_length=16)
    number = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    date = models.DateField()
    body = models.CharField(max_length=255, default='')
    text = models.CharField(max_length=255)

    class Meta:
        unique_together = (("source", "number"),)
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['body']),
            models.Index(fields=['name']),
            models.Index(fields=['source', 'number']),
        ]
