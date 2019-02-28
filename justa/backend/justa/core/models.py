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
        unique_together = (('source', 'number', 'name', 'date', 'body'),)
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['body']),
            models.Index(fields=['name']),
            models.Index(fields=['source', 'number']),
        ]


class CourtOrderESAJ(models.Model):
    source = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    decision = models.TextField()
    decision_date = models.DateField()
    status = models.TextField(default='')
    source_numbers = models.TextField(default='')
    reporter = models.TextField(default='')
    category = models.TextField(default='')
    subject = models.TextField(default='')
    petitioner = models.TextField(default='')
    petitioner_attorneys = models.TextField(default='')
    requested = models.TextField(default='')
    requested_attorneys = models.TextField(default='')
    appeals = models.TextField(default='')

    class Meta:
        ordering = ('-decision_date',)
        unique_together = (('source', 'number'))
        indexes = [
            models.Index(fields=['decision_date']),
            models.Index(fields=['number'])
        ]
