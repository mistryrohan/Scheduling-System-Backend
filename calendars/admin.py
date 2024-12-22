from django.contrib import admin
from calendars.models.calendar_model import Calendar
from calendars.models.contact_model import Contact
from calendars.models.invitee_model import Invitee
from calendars.models.timeslot_model import Timeslot

admin.site.register(Contact)
admin.site.register(Calendar)
admin.site.register(Invitee)
admin.site.register(Timeslot)
