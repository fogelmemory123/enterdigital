from django.db import models

class Participant(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='participants')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name