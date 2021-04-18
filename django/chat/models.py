from django.db import models

# Create your models here.
class ClickTracker(models.Model):
    click_count = models.IntegerField()