import pytest
from app_diversa.models import Question, Option
from app_geo.models import Country, Department
from app_diversa.factories import QuestionFactory, OptionFactory
from app_diversa.v1.serializers import ResponseSerializer

# Prueba para pregunta cerrada con opción válida
@pytest.mark.django_db
def test_closed_question_with_valid_option():
    question = QuestionFactory(question_type="closed")
    option = OptionFactory(question=question)

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": option.id
    })

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["option_selected"] == option

# Prueba para pregunta abierta con número fuera de rango
@pytest.mark.django_db
def test_open_question_with_invalid_number():
    question = QuestionFactory(data_type="integer", min_value=18, max_value=100)

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": "150"
    })

    assert not serializer.is_valid()
    assert "answer" in serializer.errors

# Casos límite

# Pregunta abierta sin respuesta
@pytest.mark.django_db
def test_open_question_without_answer():
    question = QuestionFactory(question_type="open", data_type="integer")

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": None  # No se envía respuesta
    })

    assert not serializer.is_valid()
    assert "answer" in serializer.errors

# Pregunta cerrada sin opción seleccionada
@pytest.mark.django_db
def test_closed_question_without_option_selected():
    question = QuestionFactory(question_type="closed")
    OptionFactory(question=question, text="Opción 1")

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": None  # No se selecciona ninguna opción
    })

    assert not serializer.is_valid()
    assert "option_selected" in serializer.errors  # Verifica que el error está en `option_selected`

# Valores fuera de rango
@pytest.mark.django_db
def test_open_question_out_of_range():
    question = QuestionFactory(question_type="open", data_type="integer", min_value=10, max_value=100)

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": 150  # Valor fuera de rango
    })

    assert not serializer.is_valid()
    assert "answer" in serializer.errors

# Opciones inválidas
@pytest.mark.django_db
def test_closed_question_with_invalid_option():
    question = QuestionFactory(question_type="closed")
    valid_option = OptionFactory(question=question, text="Opción válida")
    invalid_option_id = 9999  # Un ID de opción que no existe

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": invalid_option_id  # ID de una opción no válida
    })

    assert not serializer.is_valid()
    assert "answer" in serializer.errors

# Pregunta geográfica válida
@pytest.mark.django_db
def test_geographic_question():
    # Crear un país
    country = Country.objects.create(
        numeric_code=170,
        spanish_name="Colombia",
        english_name="Colombia",
        alpha_3="COL",
        alpha_2="CO"
    )

    # Crear una pregunta de tipo geográfico con rangos que incluyan el código del departamento
    question = QuestionFactory(
        is_geographic=True,
        geography_type="DEPARTMENT",
        min_value=1,
        max_value=500
    )

    # Crear un departamento vinculado al país
    department = Department.objects.create(
        code=5,
        name="Antioquia",
        country_numeric_code=country.numeric_code
    )

    # Probar el serializer con un departamento como respuesta
    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": str(department.code)  # Convertir a cadena para que coincida con el CharField del serializer
    })

    assert serializer.is_valid(), serializer.errors  # Verifica que los datos son válidos
    assert int(serializer.validated_data["answer"]) == department.code  # Convertir a entero para comparar
