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

# Prueba para pregunta abierta sin respuesta
@pytest.mark.django_db
def test_open_question_without_answer():
    question = QuestionFactory(question_type="open", data_type="integer")

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": None
    })

    assert not serializer.is_valid()
    assert "answer" in serializer.errors

# Prueba para pregunta cerrada sin opción seleccionada
@pytest.mark.django_db
def test_closed_question_without_option_selected():
    question = QuestionFactory(question_type="closed")
    OptionFactory(question=question, text_option="Opción 1")

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": None
    })

    assert not serializer.is_valid()
    assert "option_selected" in serializer.errors

# Prueba para pregunta abierta con valor fuera de rango
@pytest.mark.django_db
def test_open_question_out_of_range():
    question = QuestionFactory(question_type="open", data_type="integer", min_value=10, max_value=100)

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": 150
    })

    assert not serializer.is_valid()
    assert "answer" in serializer.errors

# Prueba para pregunta cerrada con opción inválida
@pytest.mark.django_db
def test_closed_question_with_invalid_option():
    question = QuestionFactory(question_type="closed")
    valid_option = OptionFactory(question=question, text_option="Opción válida")
    invalid_option_id = 9999

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": invalid_option_id
    })

    assert not serializer.is_valid()
    assert "answer" in serializer.errors

# Prueba para pregunta geográfica válida
@pytest.mark.django_db
def test_geographic_question():
    country = Country.objects.create(
        numeric_code=170,
        spanish_name="Colombia",
        english_name="Colombia",
        alpha_3="COL",
        alpha_2="CO"
    )

    question = QuestionFactory(
        is_geographic=True,
        geography_type="DEPARTMENT",
        min_value=1,
        max_value=500
    )

    department = Department.objects.create(
        code=5,
        name="Antioquia",
        country_numeric_code=country.numeric_code
    )

    serializer = ResponseSerializer(data={
        "question_id": question.id,
        "answer": str(department.code)
    })

    assert serializer.is_valid(), serializer.errors
    assert int(serializer.validated_data["answer"]) == department.code
