from django.contrib import admin
from .models import SurveyAttempt, Survey, Chapter, Question, SubQuestion, Option, SurveyText, Response, SystemMessage

@admin.register(SurveyAttempt)
class SurveyAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'survey', 'has_lived_in_colombia', 'birth_date', 'rejection_note', 'created_at')
    search_fields = ('user__email', 'survey__name', 'rejection_note')
    list_filter = ('created_at', 'has_lived_in_colombia', 'birth_date')

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


@admin.register(SystemMessage)
class SystemMessageAdmin(admin.ModelAdmin):
    list_display = ('key', 'title', 'is_active')
    search_fields = ('key', 'title')


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

@admin.register(SubQuestion)
class SubQuestionAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar subpreguntas (SubQuestion).
    """
    list_display = (
        'custom_identifier', 'text_subquestion', 'instruction', 'parent_question',
        'subquestion_order', 'is_required', 'is_other', 'created_at'
    )
    list_display_links = ('text_subquestion',)
    search_fields = ('custom_identifier', 'text_subquestion', 'instruction', 'parent_question__text_question')
    list_filter = ('parent_question__survey', 'is_other', 'created_at')
    ordering = ('subquestion_order',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar preguntas (Question) asociadas a encuestas, capítulos y subpreguntas.
    """
    list_display = (
        'text_question', 'instruction', 'survey', 'chapter',
        'question_type', 'matrix_layout_type','is_required', 'order_question',
        'created_at'
    )
    list_display_links = ('text_question',)
    search_fields = ('text_question', 'instruction', 'survey__name', 'chapter__name', 'matrix_layout_type',)
    list_filter = (
        'survey', 'chapter', 'question_type', 'matrix_layout_type',
        'is_required', 'created_at'
    )
    ordering = ('order_question',)
    list_select_related = ('survey', 'chapter')


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar opciones (Option) asociadas a preguntas o subpreguntas.
    """
    def get_question_id(self, obj):
        return obj.question.id if obj.question else None

    def get_subquestion_id(self, obj):
        return obj.subquestion.id if obj.subquestion else None

    get_question_id.short_description = "Question ID"
    get_subquestion_id.short_description = "SubQuestion ID"

    list_display = (
        'text_option', 'note', 'is_other', 'question', 'subquestion',
        'get_question_id', 'get_subquestion_id', 'order_option', 'created_at'
    )
    readonly_fields = ('question_id', 'subquestion_id')
    list_display_links = ('text_option',)
    search_fields = ('text_option', 'note', 'question__text_question', 'subquestion__text_subquestion')
    list_filter = ('is_other', 'created_at')
    ordering = ('-created_at',)

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
        'user', 'question', 'subquestion', 'response_text', 'response_number',
        'option_selected', 'country', 'department', 'municipality',
        'created_at'
    )
    list_display_links = ('user', 'question')
    search_fields = (
        'user__email', 'question__text_question', 'subquestion__text_subquestion',
        'response_text', 'option_selected__text_option'
    )
    list_filter = ('created_at', 'department', 'municipality')
    ordering = ('-created_at',)

