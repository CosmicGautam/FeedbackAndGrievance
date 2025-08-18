from rest_framework import serializers
from .models import State, Municipality, Feedback, Grievance, GrievanceResponse
from django.contrib.auth.models import User

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