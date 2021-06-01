from django.contrib import admin

# Register your models here.
from .models import Data, Activity


class DataAdmin(admin.ModelAdmin):
    search_fields = ['sort', 'name', 'context', 'content']


class ActivityAdmin(admin.ModelAdmin):
    search_fields = ['name', 'registration_date', 'activity_date', 'department']


admin.site.register(Data, DataAdmin)
admin.site.register(Activity, ActivityAdmin)
