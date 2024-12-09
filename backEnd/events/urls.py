# urls.py
from django.urls import path
from .views import EventAPIView,EventAdminView, EventPartAPIView

urlpatterns = [
    path('events/', EventAPIView.as_view(), name='event-list'),  # לכל האירועים
    path('events/admin/', EventAdminView.as_view(), name='event-admin'),
    path('events/admin/<path:pk>/', EventAdminView.as_view(), name='event-detail-edit-delete'),
    path('eventsPart/<int:event_id>/', EventPartAPIView.as_view(), name='event-detail'),

    path('events/<int:branch_id>/', EventAPIView.as_view(), name='events-by-branch'),  # אירועים לפי סניף
]