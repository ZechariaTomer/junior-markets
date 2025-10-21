from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Job, Application
from .forms import JobForm, ApplicationForm


class JobListView(ListView):
    """רשימת משרות"""
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10
    
    def get_queryset(self):
        return Job.objects.active().order_by('-created_at')


class JobDetailView(DetailView):
    """פרטי משרה"""
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'


class JobCreateView(LoginRequiredMixin, CreateView):
    """יצירת משרה חדשה (רק למשתמשים מחוברים)"""
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('jobs:job-list')
    
    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    """הגשת מועמדות"""
    model = Application
    form_class = ApplicationForm
    template_name = 'jobs/application_form.html'
    
    def form_valid(self, form):
        form.instance.applicant = self.request.user
        form.instance.job_id = self.kwargs['job_id']
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('jobs:job-detail', kwargs={'pk': self.kwargs['job_id']})