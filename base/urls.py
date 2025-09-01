from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
    StateViewSet, MunicipalityViewSet, CustomRegisterView,
    FeedbackAPIView, GrievanceAPIView, GrievanceListAPIView,
    GrievanceResponseAPIView, GrievanceStatusUpdateAPIView, UserProfileView
)

app_name = 'base'

router = DefaultRouter()
router.register(r'states', StateViewSet)
router.register(r'municipalities', MunicipalityViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', CustomRegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/municipalities/<int:municipality_id>/departments/<int:department_id>/feedback/', FeedbackAPIView.as_view(), name='feedback_api'),
    path('api/municipalities/<int:municipality_id>/departments/<int:department_id>/grievance/', GrievanceAPIView.as_view(), name='grievance_api'),
    path('api/grievances/', GrievanceListAPIView.as_view(), name='grievance_list_api'),
    path('api/grievances/<int:grievance_id>/respond/', GrievanceResponseAPIView.as_view(), name='grievance_response_api'),
    path('api/grievances/<int:pk>/status/', GrievanceStatusUpdateAPIView.as_view(), name='grievance_status_update_api'),
    path('api/user/profile/', UserProfileView.as_view(), name='user_profile'),
]