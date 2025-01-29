from django.contrib import admin
from .models import Diagram, DatabaseColumn, DatabaseTable, Relationship

@admin.register(Diagram)
class DiagramAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'creator', 'visibility',  'database_type']
    

admin.site.register(DatabaseTable)
admin.site.register(DatabaseColumn)
admin.site.register(Relationship)

