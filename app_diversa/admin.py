from django.contrib import admin
from .models import Survey, Chapter, Question, SubQuestion, Option, SurveyText, Response


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar encuestas (Survey) en el panel de administración.
    """
    list_display = ('name', 'title', 'description_name', 'description_title', 'created_at', 'updated_at')
    list_display_links = ('name',)
    search_fields = ('name', 'title', 'description_name', 'description_title')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar capítulos (Chapter) asociados a encuestas.
    """
    list_display = ('name', 'survey', 'description', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'survey__name', 'description')
    list_filter = ('survey', 'created_at')
    ordering = ('-created_at',)
    autocomplete_fields = ('survey',)

@admin.register(SubQuestion)
class SubQuestionAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar subpreguntas (SubQuestion).
    """
    list_display = (
        'custom_identifier', 'text_subquestion', 'instruction', 'parent_question',
        'subquestion_order', 'is_required', 'created_at'
    )
    list_display_links = ('text_subquestion',)
    search_fields = ('custom_identifier', 'text_subquestion', 'instruction', 'parent_question__text_question')
    list_filter = ('parent_question', 'created_at')
    ordering = ('subquestion_order',)
    autocomplete_fields = ('parent_question',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar preguntas (Question) asociadas a encuestas, capítulos y subpreguntas.
    """
    list_display = (
        'text_question', 'instruction', 'survey', 'chapter',
        'question_type', 'is_required', 'order_question',
        'created_at'
    )
    list_display_links = ('text_question',)
    search_fields = ('text_question', 'instruction', 'survey__name', 'chapter__name')
    list_filter = (
        'survey', 'chapter', 'question_type',
        'is_required', 'created_at'
    )
    ordering = ('order_question',)
    list_select_related = ('survey', 'chapter')


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar opciones (Option) asociadas a preguntas o subpreguntas.
    """
    list_display = (
        'text_option', 'note', 'is_other', 'question', 'subquestion', 'question_id', 'subquestion_id', 'order_option', 'created_at'
    )
    readonly_fields = ('question_id', 'subquestion_id')
    list_display_links = ('text_option',)
    search_fields = ('text_option', 'note', 'question__text_question', 'subquestion__text_subquestion')
    list_filter = ('is_other', 'created_at')
    ordering = ('-created_at',)
    autocomplete_fields = ('question', 'subquestion')


@admin.register(SurveyText)
class SurveyTextAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar textos asociados a encuestas (SurveyText).
    """
    list_display = ('title', 'survey', 'is_active', 'created_at')
    list_display_links = ('title',)
    search_fields = ('title', 'survey__name', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('-created_at',)


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar respuestas (Response) asociadas a preguntas.
    """
    list_display = (
        'user', 'question', 'response_text',
        'response_number', 'option_selected', 'options_multiple_selected', 'created_at'
    )
    list_display_links = ('user', 'question')
    search_fields = (
        'user__email', 'question__text_question', 'response_text',
        'option_selected__text_option'
    )
    list_filter = ('created_at',)
    ordering = ('-created_at',)
