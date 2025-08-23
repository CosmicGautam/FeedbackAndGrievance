from rest_framework import viewsets, generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import Group
from phonenumbers import parse, is_valid_number, format_number, PhoneNumberFormat, NumberParseException, region_code_for_number

from .models import CustomUser, State, Municipality, Department, Feedback, Grievance, GrievanceResponse
from .serializers import (
    StateSerializer, MunicipalitySerializer,
    FeedbackSerializer, GrievanceSerializer,
    GrievanceResponseSerializer
)


class CustomRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(write_only=True)
    dob = serializers.DateField(write_only=True)
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    address = serializers.CharField(write_only=True)
    contact = serializers.CharField(write_only=True)

    def validate_contact(self, value):
        """
        Validate phone number:
        - Must be a valid Nepal number (+977).
        - Normalizes to E.164 format (e.g., +9779812345678).
        """
        try:
            phone = parse(value, "NP")
            if not is_valid_number(phone):
                raise serializers.ValidationError("Invalid Nepal phone number.")
            if region_code_for_number(phone) != "NP":
                raise serializers.ValidationError("Only Nepal (+977) phone numbers are allowed.")
            return format_number(phone, PhoneNumberFormat.E164)
        except NumberParseException:
            raise serializers.ValidationError("Invalid phone number format. Use +977XXXXXXXXXX.")

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password1'],
            dob=validated_data['dob'],
            contact=validated_data['contact'],  # already normalized to +977...
            address=validated_data['address']
        )
        # Assign user to Citizens group
        citizen_group, _ = Group.objects.get_or_create(name='Citizens')
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
        return super().get_queryset()


class FeedbackAPIView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            municipality_id=self.kwargs['municipality_id'],
            department_id=self.kwargs['department_id']
        )


class GrievanceAPIView(generics.CreateAPIView):
    queryset = Grievance.objects.all()
    serializer_class = GrievanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            municipality_id=self.kwargs['municipality_id'],
            department_id=self.kwargs['department_id']
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
        serializer.save(
            user=self.request.user,
            grievance_id=self.kwargs['grievance_id']
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
        return Response(self.get_serializer(instance).data)
