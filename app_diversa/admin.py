from django.contrib import admin
from .models import Survey, Chapter, Question, Option, SurveyText, Response

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar encuestas (Survey) en el panel de administración.
    """
    # Actualizamos list_display para incluir los nuevos campos y renombramos 'description' a 'description_name'
    list_display = ('name', 'title', 'description_name', 'description_title', 'created_at', 'updated_at')
    list_display_links = ('name',)  # Permite clic en el nombre
    search_fields = ('name', 'title', 'description_name', 'description_title')  # Búsqueda avanzada
    list_filter = ('created_at', 'updated_at')  # Filtros útiles por fecha de creación/actualización
    ordering = ('-created_at',)  # Orden descendente por fecha de creación


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar capítulos (Chapter) asociados a encuestas.
    """
    list_display = ('name', 'survey', 'description', 'created_at')
    list_display_links = ('name',)  # Permite clic en el nombre
    search_fields = ('name', 'survey__name', 'description')  # Búsqueda avanzada
    list_filter = ('survey', 'created_at')  # Filtros útiles
    ordering = ('-created_at',)  # Orden descendente por fecha
    autocomplete_fields = ('survey',)  # Mejora la experiencia al seleccionar encuestas relacionadas


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar preguntas (Question) asociadas a encuestas y capítulos.
    """
    list_display = (
        'text', 'instruction', 'survey', 'chapter',
        'question_type', 'is_required', 'created_at'
    )
    list_display_links = ('text',)  # Permite clic en el texto de la pregunta
    search_fields = ('text', 'instruction', 'survey__name', 'chapter__name')  # Búsqueda avanzada
    list_filter = (
        'survey', 'chapter', 'question_type',
        'is_required', 'created_at'
    )  # Filtros útiles
    ordering = ('-created_at',)  # Orden descendente por fecha
    list_select_related = ('survey', 'chapter')  # Optimización de consultas


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar opciones (Option) asociadas a preguntas.
    """
    list_display = ('text', 'note', 'is_other', 'question', 'created_at')
    list_display_links = ('text',)  # Permite clic en el texto de la opción
    search_fields = ('text', 'note', 'question__text')  # Búsqueda por texto, nota y pregunta asociada
    list_filter = ('is_other', 'created_at')  # Filtros por opciones de tipo 'Otro' y fecha
    ordering = ('-created_at',)  # Orden descendente por fecha


@admin.register(SurveyText)
class SurveyTextAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar textos asociados a encuestas (SurveyText).
    """
    list_display = ('title', 'survey', 'is_active', 'created_at')
    list_display_links = ('title',)  # Permite clic en el título
    search_fields = ('title', 'survey__name', 'description')  # Búsqueda avanzada
    list_filter = ('is_active', 'created_at')  # Filtros por estado y fecha
    ordering = ('-created_at',)  # Orden descendente por fecha


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    """
    Configuración para gestionar respuestas (Response) asociadas a preguntas.
    """
    list_display = (
        'user', 'question', 'response_text',
        'response_number', 'option_selected', 'created_at'
    )
    list_display_links = ('user', 'question')  # Permite clic en el usuario y la pregunta
    search_fields = (
        'user__email', 'question__text', 'response_text',
        'option_selected__text'
    )  # Búsqueda avanzada
    list_filter = ('created_at',)  # Filtro por fecha de creación
    ordering = ('-created_at',)  # Orden descendente por fecha
