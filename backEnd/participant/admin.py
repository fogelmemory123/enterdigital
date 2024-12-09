from django.contrib import admin

# Register your models here.
from .models import Participant

# רישום מודלים לפאנל האדמין
admin.site.register(Participant)