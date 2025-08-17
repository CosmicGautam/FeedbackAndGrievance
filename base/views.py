from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Feedback, Grievance, GrievanceResponse, Municipality
from .serializers import FeedbackSerializer, GrievanceSerializer
import logging
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import StateSerializer, MunicipalitySerializer
from .models import State, Municipality

logger = logging.getLogger(__name__)


class StateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [AllowAny]

class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        state_id = self.request.query_params.get('state')
        if state_id:
            return Municipality.objects.filter(state_id=state_id)
        return Municipality.objects.all()

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'base/register.html'
    success_url = reverse_lazy('admin:index')

    def form_valid(self, form):
        user = form.save()
        citizen_group, _ = Group.objects.get_or_create(name='Citizens')
        user.groups.add(citizen_group)
        login(self.request, user)
        return super().form_valid(form)

class FeedbackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, municipality_id, department_id):
        if not request.user.groups.filter(name='Citizens').exists():
            logger.error(f"User {request.user.username} not in Citizens group")
            return Response({"error": "Only citizens can submit feedback"}, status=status.HTTP_403_FORBIDDEN)
        try:
            data = request.data.copy()
            data['municipality'] = municipality_id
            data['department'] = department_id
            serializer = FeedbackSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                logger.debug(f"Feedback saved for user {request.user.username}, department ID {department_id}, municipality ID {municipality_id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.error(f"Feedback invalid: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GrievanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, municipality_id, department_id):
        if not request.user.groups.filter(name='Citizens').exists():
            logger.error(f"User {request.user.username} not in Citizens group")
            return Response({"error": "Only citizens can submit grievances"}, status=status.HTTP_403_FORBIDDEN)
        try:
            data = request.data.copy()
            data['municipality'] = municipality_id
            data['department'] = department_id
            serializer = GrievanceSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                logger.debug(f"Grievance saved for user {request.user.username}, department ID {department_id}, municipality ID {municipality_id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.error(f"Grievance invalid: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error saving grievance: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GrievanceListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.groups.filter(name='Officials').exists():
            logger.error(f"User {request.user.username} not in Officials group")
            return Response({"error": "Only officials can view grievances"}, status=status.HTTP_403_FORBIDDEN)
        grievances = Grievance.objects.all().select_related('user', 'department', 'municipality')
        serializer = GrievanceSerializer(grievances, many=True)
        logger.debug(f"Grievances fetched for user {request.user.username}: {list(grievances.values('id', 'title', 'status', 'municipality__name'))}")
        return Response(serializer.data)

class GrievanceResponseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, grievance_id):
        if not request.user.groups.filter(name='Officials').exists():
            logger.error(f"User {request.user.username} not in Officials group")
            return Response({"error": "Only officials can respond to grievances"}, status=status.HTTP_403_FORBIDDEN)
        try:
            grievance = Grievance.objects.get(id=grievance_id)
            response = GrievanceResponse.objects.create(
                user=request.user,
                grievance=grievance,
                response=request.data.get('response')
            )
            logger.debug(f"Grievance response saved for grievance ID {grievance_id} by user {request.user.username}")
            return Response({"id": response.id, "response": response.response}, status=status.HTTP_201_CREATED)
        except Grievance.DoesNotExist:
            logger.error(f"Grievance with ID {grievance_id} does not exist")
            return Response({"error": "Grievance does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error saving grievance response: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GrievanceStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not request.user.groups.filter(name='Officials').exists():
            logger.error(f"User {request.user.username} not in Officials group")
            return Response({"error": "Only officials can update grievance status"}, status=status.HTTP_403_FORBIDDEN)
        try:
            grievance = Grievance.objects.get(id=pk)
            status = request.data.get('status')
            if status in [choice[0] for choice in Grievance.STATUS_CHOICES]:
                grievance.status = status
                grievance.save()
                logger.debug(f"Grievance status updated for ID {pk} to {status} by user {request.user.username}")
                return Response({"id": grievance.id, "status": grievance.status}, status=status.HTTP_200_OK)
            logger.error(f"Invalid status: {status}")
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        except Grievance.DoesNotExist:
            logger.error(f"Grievance with ID {pk} does not exist")
            return Response({"error": "Grievance does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating grievance status: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)