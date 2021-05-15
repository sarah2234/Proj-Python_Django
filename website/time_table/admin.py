from django.contrib import admin

# Register your models here.
from .models import Data


class DataAdmin(admin.ModelAdmin):
    search_fields = ['sort', 'context_ellipsis', 'name']


admin.site.register(Data, DataAdmin)
