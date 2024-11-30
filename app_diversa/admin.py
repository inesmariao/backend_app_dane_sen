from django.contrib import admin
from .models import Survey, Chapter, Question, Option, SurveyText

# Survey Admin
@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)

# Chapter Admin
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'survey', 'created_at')
    search_fields = ('name', 'survey__name')
    list_filter = ('survey',)
    autocomplete_fields = ('survey',)

# Question Admin
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'instruction', 'survey', 'chapter', 'question_type', 'is_required', 'created_at')
    search_fields = ('text', 'instruction', 'question_type', 'survey__name', 'chapter__name')
    list_filter = ('survey',  'chapter','question_type', 'is_required', 'created_at')
    ordering = ('-created_at',)
    list_select_related = ('survey',)

    def survey_name(self, obj):
        return obj.survey.name
    survey_name.short_description = 'Survey Name'


# Option Admin
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'note', 'is_other', 'question', 'created_at')
    search_fields = ('text', 'note')
    list_filter = ('is_other', 'created_at')
    ordering = ('-created_at',)

# Survey Text Admin
@admin.register(SurveyText)
class SurveyTextAdmin(admin.ModelAdmin):
    list_display = ('title', 'survey', 'is_active', 'created_at')
    search_fields = ('title', 'survey__name')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)