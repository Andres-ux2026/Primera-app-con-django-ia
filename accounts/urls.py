from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('approvals/', views.ApprovalListView.as_view(), name='approval_list'),
    path('pending/', views.DashboardRedirectView.as_view(), name='pending'),
]
