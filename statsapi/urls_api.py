from django.urls import path
from .api import RecruiterOverviewView, SeekerOverviewView

urlpatterns = [
    path("stats/recruiter/overview/", RecruiterOverviewView.as_view(), name="stats-recruiter-overview"),
    path("stats/seeker/overview/", SeekerOverviewView.as_view(), name="stats-seeker-overview"),
]
