from django.contrib import admin
from .models import Country, Department, Municipality
from django.contrib.admin import SimpleListFilter

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo `Country`.

    Permite gestionar la lista de países, con opciones de búsqueda y visualización
    de los principales campos de identificación según ISO 3166.
    """
    list_display = ('spanish_name', 'english_name', 'alpha_2', 'alpha_3', 'numeric_code')
    list_display_links = ('spanish_name', 'english_name')  # Campos clickeables
    search_fields = ('spanish_name', 'english_name', 'alpha_2', 'alpha_3')
    ordering = ('spanish_name',)  # Orden alfabético por nombre en español


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo `Department`.

    Permite gestionar los departamentos con opciones de búsqueda y visualización
    por nombre, código y país asociado.
    """
    list_display = ('name', 'code', 'country')  # Muestra nombre, código y país relacionado
    list_display_links = ('name',)  # Permite clic en el nombre
    search_fields = ('name', 'code')  # Habilita búsqueda por nombre o código
    ordering = ('name',)  # Orden alfabético por nombre

    def country(self, obj):
        """
        Devuelve el nombre del país al que pertenece el departamento.
        """
        return obj.country.spanish_name if obj.country else "No asignado"

    country.short_description = "País"


class CountryNumericCodeFilter(SimpleListFilter):
    """
    Filtro personalizado para el modelo `Municipality` basado en el país.

    Permite filtrar municipios según el código numérico del país asociado.
    """
    title = 'País (Código Numérico)'
    parameter_name = 'country_numeric_code'

    def lookups(self, request, model_admin):
        """
        Define las opciones de filtro disponibles con los códigos numéricos de los países.
        """
        countries = Country.objects.all()
        return [(country.numeric_code, country.spanish_name) for country in countries]

    def queryset(self, request, queryset):
        """
        Aplica el filtro a los municipios según el código numérico seleccionado.
        """
        if self.value():
            return queryset.filter(department__country__numeric_code=self.value())
        return queryset


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo `Municipality`.

    Permite gestionar municipios con opciones de búsqueda, visualización de
    nombre, código, departamento y filtrado por país.
    """
    list_display = ('name', 'code', 'department', 'country_name')  # Campos visibles
    list_display_links = ('name',)  # Clickeable en el nombre
    search_fields = ('name', 'code')  # Habilita búsqueda por nombre o código
    list_filter = (CountryNumericCodeFilter,)  # Filtro por país (código numérico)
    ordering = ('name',)  # Orden alfabético por nombre

    def country_name(self, obj):
        """
        Devuelve el nombre del país al que pertenece el municipio.
        """
        return obj.department.country.spanish_name if obj.department and obj.department.country else "No asignado"

    country_name.short_description = "País"
