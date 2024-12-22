from django.urls import path
from calendars.views.calendar_detail_view import CalendarDetailView
from calendars.views.calendar_list_view import CalendarListView
from calendars.views.finalize_view import FinalizeView
from calendars.views.timeslot_detail_view import TimeslotDetailView
from calendars.views.timeslot_list_view import TimeslotListView
from calendars.views.invitee_view import InviteeView
from calendars.views.invitation_view import InvitationView
from calendars.views.reminder_view import ReminderView

from calendars.views.invitation_view2 import InvitationView2
from calendars.views.timeslot_list_view2 import TimeslotListView2


app_name = 'calendars'
urlpatterns = [
    path('', CalendarListView.as_view(), name='calendar_list_view'),
    path('<int:calendar_id>/details/', CalendarDetailView.as_view(), name='calendar_detail_view'),
    path('<int:calendar_id>/timeslots/', TimeslotListView.as_view(), name='timeslot_list_view'),
    path('timeslots/<int:timeslot_id>/', TimeslotDetailView.as_view(), name='timeslot_detail_view'),
    path('<int:calendar_id>/finalize/', FinalizeView.as_view(), name='finalize_view'),
    path('<int:calendar_id>/invitee/<int:user_id>/', InviteeView.as_view(), name="invitee_view"),
    path('<int:calendar_id>/finalize/', FinalizeView.as_view(), name='finalize_view'),
    path('<int:calendar_id>/invitations/', InvitationView.as_view(), name='invitation_view'),
    path('<int:calendar_id>/reminders/', ReminderView.as_view(), name='reminder_view'),
    path('<int:calendar_id>/invitations2/', InvitationView2.as_view(), name='invitation_view2'),
    path('<int:calendar_id>/timeslots2/', TimeslotListView2.as_view(), name='timeslot_list_view2'),
]