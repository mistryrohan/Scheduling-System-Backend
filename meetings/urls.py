from django.urls import path
from meetings.views.meetings_view import MeetingsView
from meetings.views.details_view import DetailsView

app_name = 'meetings'
urlpatterns = [
    path('', MeetingsView.as_view(), name="meeting_list"),
    path('<int:meeting_id>/', DetailsView.as_view(), name="meeting_details"),
]