from django.urls import path
from .views import UserBirthdayView, LoginView,RegisterView,UserBirthdayAdminView,GetUserNameView

urlpatterns = [
    # path('birthdays/<int:branch_id/', UserBirthdayView.as_view(), name='user-list1'),
    path('birthdays/<int:branch_id>/', UserBirthdayView.as_view(), name='user-detail1'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    # path('admin/birthday/',UserBirthdayAdminView.as_view(), name='admin-birthday')
    path('admin/birthday/', UserBirthdayAdminView.as_view(), name='user-birthday-list'),
    path('admin/birthday/<int:pk>/', UserBirthdayAdminView.as_view(), name='user-birthday-detail1'),
    path('get-username/', GetUserNameView.as_view(), name='get_username'),

]