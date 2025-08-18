from django.shortcuts import render
from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import State, Municipality, Department, Feedback, Grievance, GrievanceResponse
from .serializers import StateSerializer, MunicipalitySerializer, FeedbackSerializer, GrievanceSerializer, GrievanceResponseSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework import status

class CustomRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],  # Use email as username for compatibility
            email=validated_data['email'],
            password=validated_data['password1']
        )
        # Assign user to Citizen group
        citizen_group, created = Group.objects.get_or_create(name='Citizens')
        user.groups.add(citizen_group)
        return user

class CustomRegisterView(generics.CreateAPIView):
    serializer_class = CustomRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = TokenObtainPairSerializer.get_token(user)
        return Response({
            'access': str(token.access_token),
            'refresh': str(token),
        }, status=status.HTTP_201_CREATED)

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [permissions.AllowAny]

class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        state_id = self.request.query_params.get('state')
        if state_id:
            return Municipality.objects.filter(state_id=state_id)
        return Municipality.objects.all()

class FeedbackAPIView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        municipality_id = self.kwargs['municipality_id']
        department_id = self.kwargs['department_id']
        serializer.save(
            user=self.request.user,
            municipality_id=municipality_id,
            department_id=department_id
        )

class GrievanceAPIView(generics.CreateAPIView):
    queryset = Grievance.objects.all()
    serializer_class = GrievanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        municipality_id = self.kwargs['municipality_id']
        department_id = self.kwargs['department_id']
        serializer.save(
            user=self.request.user,
            municipality_id=municipality_id,
            department_id=department_id
        )

class GrievanceListAPIView(generics.ListAPIView):
    queryset = Grievance.objects.all()
    serializer_class = GrievanceSerializer
    permission_classes = [permissions.IsAuthenticated]

class GrievanceResponseAPIView(generics.CreateAPIView):
    queryset = GrievanceResponse.objects.all()
    serializer_class = GrievanceResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        grievance_id = self.kwargs['grievance_id']
        serializer.save(
            user=self.request.user,
            grievance_id=grievance_id
        )

class GrievanceStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = Grievance.objects.all()
    serializer_class = GrievanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = request.data.get('status', instance.status)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)