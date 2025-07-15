from django.db import models

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)