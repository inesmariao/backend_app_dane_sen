from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """
    Configuración personalizada para el modelo de usuario en el panel de administración.
    
    Incluye la gestión de usuarios registrados con email, nombre de usuario (username)
    o número de celular como identificadores únicos. Permite la visualización,
    edición, eliminación lógica y filtrado de usuarios.
    """
    model = CustomUser

    # Campos visibles en la lista principal del panel de administración
    list_display = (
        'email',
        'username',
        'phone_number',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at'
    )
    list_display_links = ('email', 'username')  # Campos clickeables
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at'
    )  # Filtros disponibles en el panel de usuarios
    search_fields = (
        'email',
        'username',
        'phone_number'
    )  # Campos que pueden ser buscados
    ordering = ('created_at',)  # Orden predeterminado por fecha de creación

    # Configuración de las secciones y campos al editar/ver un usuario
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'phone_number', 'password'),
            'description': "Campos básicos del usuario. Incluye los identificadores principales y la contraseña."
        }),
        ('Información Personal', {
            'fields': ('name', 'last_name'),
            'description': "Información personal adicional del usuario."
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': "Gestión de permisos y roles asignados al usuario."
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'created_at'),
            'description': "Tiempos relacionados con la actividad y creación del usuario."
        }),
    )

    # Configuración de las secciones y campos al añadir un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'phone_number',
                'password1',
                'password2',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
            'description': "Campos para crear un nuevo usuario. Incluye permisos y roles opcionales."
        }),
    )

    # Campos de solo lectura
    readonly_fields = ('created_at',)

# Registrar el modelo de usuario personalizado en el panel de administración
admin.site.register(CustomUser, CustomUserAdmin)
