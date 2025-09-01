from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group
from .models import State, Municipality, Feedback, Grievance, GrievanceResponse, CustomUser
from .serializers import (
    StateSerializer, MunicipalitySerializer, FeedbackSerializer,
    GrievanceSerializer, GrievanceResponseSerializer, CustomRegisterSerializer
)
from .permissions import IsOfficialForMunicipality

class CustomRegisterView(generics.CreateAPIView):
    serializer_class = CustomRegisterSerializer

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticated]

class MunicipalityViewSet(viewsets.ModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        state_id = self.request.query_params.get('state')
        if state_id:
            queryset = queryset.filter(state_id=state_id)
        return queryset

class FeedbackAPIView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GrievanceAPIView(generics.CreateAPIView):
    queryset = Grievance.objects.all()
    serializer_class = GrievanceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GrievanceListAPIView(generics.ListAPIView):
    serializer_class = GrievanceSerializer
    permission_classes = [IsOfficialForMunicipality]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Officials').exists() and user.municipality:
            return Grievance.objects.filter(municipality=user.municipality)
        return Grievance.objects.filter(user=user)  # Citizens see their own grievances

class GrievanceResponseAPIView(generics.CreateAPIView):
    queryset = GrievanceResponse.objects.all()
    serializer_class = GrievanceResponseSerializer
    permission_classes = [IsOfficialForMunicipality]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GrievanceStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = Grievance.objects.all()
    serializer_class = GrievanceSerializer
    permission_classes = [IsOfficialForMunicipality]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={'status': request.data.get('status')}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        is_official = user.groups.filter(name='Officials').exists()
        data = {
            'username': user.username,
            'email': user.email,
            'is_official': is_official,
            'municipality': user.municipality.id if user.municipality else None,
            'municipality_name': user.municipality.name if user.municipality else None,
        }
        return Response(data)