from django.contrib import admin
from .models import Survey, Question, Option, Module
from users.models import CustomUser

# CustomUser Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email',)
    list_filter = ('is_active', 'is_staff', 'created_at')
    ordering = ('-created_at',)

# Survey Admin
@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# Question Admin
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'is_required', 'survey', 'created_at')
    search_fields = ('text', 'question_type', 'survey__name')
    list_filter = ('survey', 'question_type', 'is_required', 'created_at')
    ordering = ('-created_at',)
    list_select_related = ('survey',)
    
    def survey_name(self, obj):
        return obj.survey.name
    survey_name.short_description = 'Survey Name'

# Option Admin
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_other', 'question', 'created_at')
    search_fields = ('text',)
    list_filter = ('is_other', 'created_at')
    ordering = ('-created_at',)

# Module Admin
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)