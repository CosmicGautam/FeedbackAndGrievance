from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'base'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/municipalities/<int:municipality_id>/departments/<int:department_id>/feedback/', views.FeedbackAPIView.as_view(), name='feedback_api'),
    path('api/municipalities/<int:municipality_id>/departments/<int:department_id>/grievance/', views.GrievanceAPIView.as_view(), name='grievance_api'),
    path('api/grievances/', views.GrievanceListAPIView.as_view(), name='grievance_list_api'),
    path('api/grievances/<int:grievance_id>/respond/', views.GrievanceResponseAPIView.as_view(), name='grievance_response_api'),
    path('api/grievances/<int:pk>/status/', views.GrievanceStatusUpdateAPIView.as_view(), name='grievance_status_update_api'),
]