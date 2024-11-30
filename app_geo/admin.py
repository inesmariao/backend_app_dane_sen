from django.contrib import admin
from .models import Country, Department, Municipality
from django.contrib.admin import SimpleListFilter

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('spanish_name', 'english_name', 'alpha_2', 'alpha_3', 'numeric_code')
    search_fields = ('spanish_name', 'english_name', 'alpha_2', 'alpha_3')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country')
    search_fields = ('name', 'code')

class CountryNumericCodeFilter(SimpleListFilter):
    title = 'País (Código Numérico)'
    parameter_name = 'country_numeric_code'

    def lookups(self, request, model_admin):
        # Devuelve las opciones de filtro con los códigos numéricos
        countries = Country.objects.all()
        return [(country.numeric_code, country.english_name) for country in countries]

    def queryset(self, request, queryset):
        # Filtra los municipios por el código numérico del país
        if self.value():
            return queryset.filter(department__country__numeric_code=self.value())
        return queryset

@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department')
    search_fields = ('name', 'code')
    list_filter = (CountryNumericCodeFilter,)