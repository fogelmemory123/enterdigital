from django.db import models

class Branch(models.Model):
    city = models.CharField(max_length=100, unique=True)
    address = models.TextField()

    def __str__(self):
        return self.city
from django.db import models

# Create your models here.
