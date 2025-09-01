from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import State, Municipality, Department, Feedback, Grievance, GrievanceResponse, CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'contact', 'municipality', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups', 'municipality')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('dob', 'contact', 'address', 'municipality')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'dob', 'contact', 'address', 'municipality', 'is_staff', 'is_active', 'groups'),
        }),
    )
    search_fields = ('username', 'email', 'contact')

class StateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    search_fields = ('name',)
    list_filter = ('state',)

try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Municipality, MunicipalityAdmin)
admin.site.register(Department)
admin.site.register(Feedback)
admin.site.register(Grievance)
admin.site.register(GrievanceResponse)