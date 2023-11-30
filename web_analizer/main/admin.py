from django.contrib import admin
from .models import DemographyEntry

@admin.register(DemographyEntry)
class DemographyEntryAdmin(admin.ModelAdmin):
    list_display = ('region', 'source', 'year', 'total_population', 'births', 'deaths', 'migration')
    list_filter = ('region', 'source')
    search_fields = ('region', 'source')
