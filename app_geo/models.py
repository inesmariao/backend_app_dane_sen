from django.db import models

class Country(models.Model):
    spanish_name = models.CharField(
        max_length=100,
        help_text="Nombre del país en español (Ej: 'Afganistán')."
    )
    english_name = models.CharField(
        max_length=100,
        help_text="Nombre del país en inglés (Ej: 'Afghanistan')."
    )
    alpha_3 = models.CharField(
        max_length=3,
        unique=True,
        help_text="Código Alpha-3 del país según ISO 3166 (Ej: 'AFG')."
    )
    alpha_2 = models.CharField(
        max_length=2,
        unique=True,
        help_text="Código Alpha-2 del país según ISO 3166 (Ej: 'AF')."
    )
    numeric_code = models.PositiveIntegerField(
        unique=True,
        help_text="Código numérico del país según ISO 3166 (Ej: '4')."
    )

    def __str__(self):
        return self.spanish_name

class Department(models.Model):
    code = models.PositiveIntegerField(
        unique=True,
        help_text="Código único del departamento (Ej: '05' para Antioquia)."
    )
    name = models.CharField(
        max_length=100,
        help_text="Nombre del departamento (Ej: 'Antioquia')."
    )
    country_numeric_code = models.PositiveIntegerField(
        help_text="Código numérico del país al que pertenece este departamento, enlazado por 'numeric_code' de Country."
    )

    def __str__(self):
        return self.name

    @property
    def country(self):
        """
        Devuelve el objeto Country relacionado mediante `country_numeric_code`.
        """
        return Country.objects.get(numeric_code=self.country_numeric_code)

class Municipality(models.Model):
    code = models.PositiveIntegerField(
        unique=True,
        help_text="Código único del municipio (Ej: '5001' para Medellín')."
    )
    name = models.CharField(
        max_length=100,
        help_text="Nombre del municipio (Ej: 'Medellín')."
    )
    department_code = models.PositiveIntegerField(
        help_text="Código del departamento al que pertenece este municipio, enlazado con 'code' de Department."
    )

    def __str__(self):
        return self.name

    @property
    def department(self):
        """
        Devuelve el objeto `Department` relacionado según `department_code`.
        """
        return Department.objects.get(code=self.department_code)

