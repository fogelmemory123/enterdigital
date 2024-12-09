from django.db import models
from users.models import User  # Import from the users app (if you separate users into another app)
from branches.models import Branch

class Event(models.Model):
    date = models.DateTimeField()
    description = models.TextField()
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='events')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')

    def __str__(self):
        return f"{self.description} - {self.date}"


