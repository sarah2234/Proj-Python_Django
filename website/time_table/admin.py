from django.contrib import admin

# Register your models here.
from .models import Data, TimeTable


class DataAdmin(admin.ModelAdmin):
    search_fields = ['sort', 'context_ellipsis', 'name']


class TimeTableAdmin(admin.ModelAdmin):
    search_fields = ['prof', 'subject', 'date', 'start_h', 'end_h']


admin.site.register(Data, DataAdmin)
admin.site.register(TimeTable, TimeTableAdmin)
