from rest_framework import serializers
from .models import State, Municipality, Feedback, Grievance, GrievanceResponse, CustomUser

class CustomRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    address = serializers.CharField(required=True)
    contact = serializers.CharField(required=True)
    municipality = serializers.PrimaryKeyRelatedField(
        queryset=Municipality.objects.all(),
        required=False,
        allow_null=True
    )  # Optional for all users during registration

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
            contact=validated_data['contact'],
            address=validated_data['address'],
            municipality=validated_data.get('municipality')
        )
        return user

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name']

class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = ['id', 'name', 'state']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'rating', 'comment', 'municipality', 'department', 'user']
        read_only_fields = ['user']

class GrievanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grievance
        fields = ['id', 'title', 'description', 'status', 'municipality', 'department', 'user']
        read_only_fields = ['user', 'status']

class GrievanceResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrievanceResponse
        fields = ['id', 'response', 'grievance', 'user']
        read_only_fields = ['user']