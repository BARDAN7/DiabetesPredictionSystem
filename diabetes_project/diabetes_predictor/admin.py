from django.contrib import admin
from .models import DiabetesHistory, Profile

admin.site.register(Profile)
@admin.register(DiabetesHistory)
class DiabetesHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender','hba1c_level','blood_glucose_level', 'result', 'medicine', 'created_at')
    list_filter = ('result', 'gender', 'created_at')
    search_fields = ('user__username', 'user__email')
