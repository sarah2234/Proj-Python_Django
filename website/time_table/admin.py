from django.contrib import admin

# Register your models here.
from .models import Data, Activity, Profile


class DataAdmin(admin.ModelAdmin):
    search_fields = ['sort', 'name', 'context', 'content']


class ActivityAdmin(admin.ModelAdmin):
    search_fields = ['name', 'registration_date', 'activity_date', 'department']


class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user', 'student_ID', 'CBNU_PW']


admin.site.register(Data, DataAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Profile, ProfileAdmin)
