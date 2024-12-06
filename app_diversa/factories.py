import factory
from app_diversa.models import Survey, Chapter, Question, Option
from app_geo.models import Country, Department, Municipality

class SurveyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Survey

    name = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph')

class ChapterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Chapter

    survey = factory.SubFactory(SurveyFactory)
    name = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('paragraph')

class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    survey = factory.SubFactory(SurveyFactory)
    chapter = factory.SubFactory(ChapterFactory)
    text = factory.Faker('sentence', nb_words=6)
    question_type = 'open'  # Valores posibles: 'open', 'closed'
    data_type = 'integer'   # Valores posibles: 'integer', 'text'
    min_value = 10
    max_value = 100
    is_geographic = False
    geography_type = None

class OptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Option

    question = factory.SubFactory(QuestionFactory)
    text = factory.Faker('word')
    is_other = False

class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country

    code = factory.Faker('ean', length=8)  # Código ficticio
    name = factory.Faker('country')

class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    code = factory.Faker('numerify', text="###")  # Código numérico ficticio
    name = factory.Faker('state')
    country = factory.SubFactory(CountryFactory)

class MunicipalityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Municipality

    code = factory.Faker('numerify', text="#####")
    name = factory.Faker('city')
    department = factory.SubFactory(DepartmentFactory)
