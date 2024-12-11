import factory
from app_diversa.models import Survey, Chapter, Question, Option
from app_geo.models import Country, Department, Municipality

class SurveyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Survey

    name = factory.Faker('sentence', nb_words=4)
    description_name = factory.Faker('paragraph')
    description_title = factory.Faker('sentence', nb_words=6)


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
    text_question = factory.Faker('sentence', nb_words=6)
    question_type = 'open'
    data_type = 'integer'
    min_value = 0
    max_value = 10000
    is_geographic = False
    geography_type = None
    is_multiple = False
    order_question = factory.Sequence(lambda n: n)


class OptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Option

    question = factory.SubFactory(QuestionFactory)
    text_option = factory.Faker('word')
    is_other = False
    order_option = factory.Sequence(lambda n: n)
    order_question = factory.Sequence(lambda n: n)


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country

    code = factory.Faker('ean', length=8)
    name = factory.Faker('country')


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    code = factory.Faker('numerify', text="###")
    name = factory.Faker('state')
    country = factory.SubFactory(CountryFactory)


class MunicipalityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Municipality

    code = factory.Faker('numerify', text="#####")
    name = factory.Faker('city')
    department = factory.SubFactory(DepartmentFactory)
