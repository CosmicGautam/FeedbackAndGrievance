from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('municipalities/<int:pk>/departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/<int:pk>/feedback/', views.FeedbackCreateView.as_view(), name='feedback_create'),
    path('departments/<int:pk>/grievance/', views.GrievanceCreateView.as_view(), name='grievance_create'),
    path('grievances/<int:pk>/', views.GrievanceDetailView.as_view(), name='grievance_detail'),
    path('login/', LoginView.as_view(template_name='base/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='base:home'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('grievances/', views.GrievanceListView.as_view(), name='grievance_list'),
    path('grievances/<int:grievance_id>/respond/', views.GrievanceResponseCreateView.as_view(), name='grievance_response_create'),
    path('grievances/<int:pk>/status/', views.GrievanceStatusUpdateView.as_view(), name='grievance_status_update'),
]