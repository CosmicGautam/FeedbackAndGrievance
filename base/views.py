from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import Group
from .models import State, Municipality, Department, Feedback, Grievance, GrievanceResponse
import logging

# Set up logging
logger = logging.getLogger(__name__)

class HomeView(ListView):
    model = State
    template_name = 'base/home.html'
    context_object_name = 'states'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['states'] = State.objects.prefetch_related('municipalities').all()
        logger.debug('Fetched states: %s', context['states'])
        return context

class DepartmentListView(ListView):
    model = Department
    template_name = 'base/department_list.html'
    context_object_name = 'departments'

    def get_queryset(self):
        try:
            municipality_id = self.kwargs['pk']
            logger.debug(f"Fetching departments for municipality ID: {municipality_id}")
            municipality = Municipality.objects.get(id=municipality_id)
            return Department.objects.filter(municipality_id=municipality_id).select_related('municipality')
        except Municipality.DoesNotExist:
            logger.error(f"Municipality with ID {municipality_id} does not exist")
            raise Http404("Municipality does not exist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['municipality'] = Municipality.objects.get(id=self.kwargs['pk'])
        except Municipality.DoesNotExist:
            logger.error(f"Municipality with ID {self.kwargs['pk']} does not exist for context")
            raise Http404("Municipality does not exist")
        return context

class FeedbackCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Feedback
    fields = ['rating', 'comment']
    template_name = 'base/feedback_grievance.html'
    permission_required = 'base.add_feedback'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['department'] = Department.objects.get(id=self.kwargs['pk'])
        context['form_type'] = 'feedback'
        return context

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='Citizens').exists():
            raise Http404("Only citizens can submit feedback")
        form.instance.user = self.request.user
        form.instance.department_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('base:department_list', kwargs={'pk': self.object.department.municipality_id})

class GrievanceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Grievance
    fields = ['title', 'description']
    template_name = 'base/feedback_grievance.html'
    permission_required = 'base.add_grievance'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['department'] = Department.objects.get(id=self.kwargs['pk'])
        context['form_type'] = 'grievance'
        return context

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='Citizens').exists():
            raise Http404("Only citizens can submit grievances")
        form.instance.user = self.request.user
        form.instance.department_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('base:department_list', kwargs={'pk': self.object.department.municipality_id})

class GrievanceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Grievance
    template_name = 'base/grievance_list.html'
    context_object_name = 'grievances'
    permission_required = 'base.view_grievance'

    def get_queryset(self):
        if not self.request.user.groups.filter(name='Officials').exists():
            raise Http404("Only officials can view grievances")
        return Grievance.objects.all().select_related('user', 'department')

class GrievanceDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Grievance
    template_name = 'base/grievance_detail.html'
    permission_required = 'base.view_grievance'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['responses'] = self.object.responses.all()
        context['is_official'] = self.request.user.groups.filter(name='Officials').exists()
        return context

class GrievanceResponseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = GrievanceResponse
    fields = ['response']
    template_name = 'base/grievance_response_form.html'
    permission_required = 'base.add_grievanceresponse'

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='Officials').exists():
            raise Http404("Only officials can respond to grievances")
        form.instance.user = self.request.user
        form.instance.grievance_id = self.kwargs['grievance_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('base:grievance_detail', kwargs={'pk': self.kwargs['grievance_id']})

class GrievanceStatusUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Grievance
    fields = ['status']
    template_name = 'base/grievance_status_form.html'
    permission_required = 'base.change_grievance'

    def form_valid(self, form):
        if not self.request.user.groups.filter(name='Officials').exists():
            raise Http404("Only officials can update grievance status")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('base:grievance_detail', kwargs={'pk': self.kwargs['pk']})

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'base/register.html'
    success_url = reverse_lazy('base:home')

    def form_valid(self, form):
        user = form.save()
        citizen_group, _ = Group.objects.get_or_create(name='Citizens')
        user.groups.add(citizen_group)
        login(self.request, user)
        return super().form_valid(form)