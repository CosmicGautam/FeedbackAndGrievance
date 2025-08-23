from rest_framework import serializers
from .models import State, Municipality, Feedback, Grievance, GrievanceResponse, CustomUser
from django.contrib.auth.models import Group


class CustomRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(write_only=True)
    dob = serializers.DateField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    contact = serializers.CharField(write_only=True)

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
            address=validated_data['address']
        )
        citizen_group, created = Group.objects.get_or_create(name='Citizens')
        user.groups.add(citizen_group)
        return user

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name']

class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = ['id', 'name']

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