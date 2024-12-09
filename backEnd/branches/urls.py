from django.urls import path
from .views import BranchListCreateAPIView,BranchAdminView

urlpatterns = [
    path('branches/', BranchListCreateAPIView.as_view(), name='branch-list-create'),
    path('branches/<int:id>/', BranchListCreateAPIView.as_view(), name='branch-detail'),
    path('branches/admin/', BranchAdminView.as_view(), name='branch-admin'),

]