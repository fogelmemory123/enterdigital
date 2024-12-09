from django.urls import path
from .views import ParticipantAPIView

urlpatterns = [
    path('events/<int:event_id>/participants/', ParticipantAPIView.as_view(), name='event-participants'),
    path('event/<int:event_id>/', ParticipantAPIView.as_view(), name='event-details'),
    path('events/<int:event_id>/participants/<int:participant_id>/', ParticipantAPIView.as_view(),
         name='participant-detail'),

]
