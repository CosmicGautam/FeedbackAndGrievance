from django.contrib import admin
from .models import State, Municipality, Department, Feedback, Grievance
# Register your models here.

admin.site.register(State)
admin.site.register(Municipality)
admin.site.register(Department)
admin.site.register(Feedback)
admin.site.register(Grievance)
