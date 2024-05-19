# Django Ninja CRUD
[![Tests](https://github.com/hbakri/django-ninja-crud/actions/workflows/tests.yml/badge.svg)](https://github.com/hbakri/django-ninja-crud/actions)
[![Coverage](https://img.shields.io/codecov/c/github/hbakri/django-ninja-crud/main.svg?label=coverage&logo=codecov&logoColor=white)](https://codecov.io/gh/hbakri/django-ninja-crud)
[![PyPI version](https://img.shields.io/pypi/v/django-ninja-crud?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/django-ninja-crud/)
[![Downloads](https://static.pepy.tech/badge/django-ninja-crud/month)](https://pepy.tech/project/django-ninja-crud)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![MyPy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://github.com/python/mypy)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

![Django Ninja CRUD](https://raw.githubusercontent.com/hbakri/django-ninja-crud/main/docs/assets/images/django-ninja-crud-cover.png)

> [!IMPORTANT]
> With the release of version `0.5`, Django Ninja CRUD introduces significant
> and breaking changes. Users are strongly advised to pin their requirements to the
> appropriate version to ensure compatibility with their projects.

Django Ninja CRUD is a powerful, [declarative](https://en.wikipedia.org/wiki/Declarative_programming), and yet a little bit opinionated framework that
simplifies the development of **CRUD** ([**C**reate, **R**ead, **U**pdate, **D**elete](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete))
endpoints with [Django Ninja](https://github.com/vitalik/django-ninja), and also
provides a declarative scenario-based way for testing these endpoints with
[Django REST Testing](https://github.com/hbakri/django-rest-testing) _(the little brother of this package)_ 🐣.

It allows you to define common endpoints as class-based views and customize them to
conform to your project's conventions with ease, and also create easily your own
custom views and declare them alongside the provided CRUD views, fostering modularity
and extensibility. This package promotes focusing on what matters most:
**solving real problems**, not reinventing the wheel all over your project.

Initially inspired by DRF's [ModelViewSet](https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset),
Django Ninja CRUD evolved to address its limitations, adopting a
[composition-over-inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance)
approach to achieve true modularity – a foundational step towards a broader declarative
interface for endpoint creation.

Key challenges with inheritance-based viewsets:
- **Unicity of CRUD endpoints per model**: Django Ninja CRUD allows you to define multiple endpoints for the same model, enabling versioning or alternative representations.
- **Customization inflexibility**: Instead of overriding methods on a monolithic class, you can customize individual views through composition and configuration.
- **Implicit relations within inheritance hierarchies**: Composition decouples views, reducing dependencies and promoting reusability.
- **Lack of modularity for new endpoints**: Adding custom endpoints no longer requires subclassing the entire viewset, making it easier to introduce new functionality incrementally.

## ✨ Key Features
- **Purely Declarative**: Define views and tests by declaring what you want, not how to do it.
- **Unmatched Modularity**: Tailor your viewsets with desired CRUD views, customize each view's behavior.
- **Easy to Extend**: Create your own custom views and use them alongside the provided CRUD views as reusable components.
- **Scenario-based Testing Framework**: Leverage a scenario-based testing framework for defining diverse test cases declaratively and concisely.
- **Focus on What Matters**: Spend more time solving real-world problems and less on common and repetitive tasks.

> **Django Ninja CRUD is not just a tool; it's a paradigm shift in Django web application development and testing.**

## 📝 Requirements

[![Python versions](https://img.shields.io/pypi/pyversions/django-ninja-crud.svg?color=306998&label=python&logo=python&logoColor=white)](https://github.com/python/cpython)
[![Django versions](https://img.shields.io/badge/3.2_|_4.1_|_4.2_|_5.0-blue?color=0C4B33&label=django&logo=django&logoColor=white)](https://github.com/django/django)
[![Django Ninja versions](https://img.shields.io/badge/1.0_|_1.1-blue?color=black&label=django-ninja&logo=fastapi&logoColor=white)](https://github.com/vitalik/django-ninja)

## ⚒️ Installation
```bash
pip install django-ninja-crud[testing]
```
For more information, see the [installation guide](https://django-ninja-crud.readme.io/docs/02-installation).

## 🌞 How It Works

Let's imagine you're building a system for a university and you have a model called `Department`. Each department in your university has a unique title.

```python
# examples/models.py
from django.db import models

class Department(models.Model):
    title = models.CharField(max_length=255, unique=True)
```

To interact with this data, we need a way to convert it between Python objects and a format that's easy to read and write (like JSON). In Django Ninja, we do this with `Schema`:

```python
# examples/schemas.py
from ninja import Schema

class DepartmentIn(Schema):
    title: str

class DepartmentOut(Schema):
    id: int
    title: str
```

The `DepartmentIn` schema defines what data we need when creating or updating a department. The `DepartmentOut` schema defines what data we'll provide when retrieving a department.

Now, here comes the power of the package. With it, you can set up the **CRUD**
operations for the `Department` model with just a few lines of code:

```python
# examples/views/department_views.py
from typing import List
from django.http import HttpRequest
from ninja import NinjaAPI
from ninja_crud import views, viewsets

from examples.models import Department
from examples.schemas import DepartmentIn, DepartmentOut

api = NinjaAPI()


class DepartmentViewSet(viewsets.APIViewSet):
    api = api
    model = Department

    list_departments = views.ListView(
        response_body=List[DepartmentOut]
    )
    create_department = views.CreateView(
        request_body=DepartmentIn,
        response_body=DepartmentOut,
    )
    read_department = views.ReadView(
        response_body=DepartmentOut
    )
    update_department = views.UpdateView(
        request_body=DepartmentIn,
        response_body=DepartmentOut,
    )
    delete_department = views.DeleteView()


# Beyond the CRUD operations managed by the viewset,
# the api or router can be used in the standard Django Ninja way
@api.get("/statistics/", response=dict)
def get_department_statistics(request: HttpRequest):
    return {"total": Department.objects.count()}
```

And if your viewset is as simple as the one above, you can leverage the `APIViewSet`
class to define it in a more concise way, with default request and response bodies:
```python
# examples/views/department_views.py
from ninja import NinjaAPI
from ninja_crud import views, viewsets

from examples.models import Department
from examples.schemas import DepartmentIn, DepartmentOut

api = NinjaAPI()


class DepartmentViewSet(viewsets.APIViewSet):
    api = api
    model = Department
    default_request_body = DepartmentIn
    default_response_body = DepartmentOut

    list_departments = views.ListView()
    create_department = views.CreateView()
    read_department = views.ReadView()
    update_department = views.UpdateView()
    delete_department = views.DeleteView()
```

## ☔️ Scenario-based Testing

Django Ninja CRUD integrates seamlessly with [Django REST Testing](https://github.com/hbakri/django-rest-testing),
and ensures comprehensive coverage and robust validation of your CRUD endpoints. At
first, the testing framework was part of this package, but it was later extracted
to its own package to allow for more flexibility and to be used with other Django
REST frameworks than Django Ninja.

With this package, you can:
- **Declaratively Define Test Scenarios**: Specify expected request and response details for each scenario, making your tests self-documenting and easy to understand.
- **Test Diverse Conditions**: Validate endpoint behaviors under various conditions, including valid and invalid inputs, nonexistent resources, and custom business rules.
- **Enhance Clarity and Maintainability**: Break tests into modular, manageable units, improving code organization and reducing technical debt.
- **Ensure Comprehensive Coverage**: Rigorously test your endpoints, leaving no stone unturned, thanks to the scenario-based approach.

To handle exceptions like `ObjectDoesNotExist` and return appropriate responses in your
tests, you can define an exception handler like this:

```python
# examples/exception_handlers.py
from ninja import NinjaAPI
from django.core.exceptions import ObjectDoesNotExist

api = NinjaAPI()


@api.exception_handler(ObjectDoesNotExist)
def handle_object_does_not_exist(request, exc):
    return api.create_response(
        request,
        {"message": "ObjectDoesNotExist", "detail": str(exc)},
        status=404,
    )

# ... other exception handlers
```

Now, you can write tests for your CRUD views using the scenario-based testing framework:

```python
# examples/tests/test_department_views.py
from examples.models import Department
from examples.schemas import DepartmentOut

from ninja_crud.testing import APITestCase, APIViewTestScenario


class TestDepartmentViewSet(APITestCase):
    department: Department

    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(title="department")

    def test_read_department(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/departments/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department.id},
                    expected_response_status=200,
                    expected_response_body_type=DepartmentOut,
                    expected_response_body={
                        "id": self.department.id,
                        "title": self.department.title,
                    },
                ),
                APIViewTestScenario(
                    path_parameters={"id": 9999},
                    expected_response_status=404,
                ),
            ],
        )
```

By combining Django Ninja CRUD's declarative views with Django REST Testing's
scenario-based testing capabilities, you can confidently build and maintain robust,
well-tested RESTful APIs with ease.

## 📚 Documentation
For more information, see the [documentation](https://django-ninja-crud.readme.io/).

## 🫶 Support
First and foremost, a heartfelt thank you to the 400+ stargazers who have shown their support for this project. Your recognition and belief in its potential fuel my drive to maintain and improve this work, making it more visible to new potential users and contributors.

[![Star History Chart](https://api.star-history.com/svg?repos=hbakri/django-ninja-crud&type=Date)](https://star-history.com/#hbakri/django-ninja-crud&Date)

If you've benefited from this project or appreciate the dedication behind it, consider showing further support. Whether it's the price of a coffee, a word of encouragement, or a sponsorship, every gesture adds fuel to the open-source fire, making it shine even brighter. ✨

[![Sponsor](https://img.shields.io/badge/sponsor-donate-pink?logo=github-sponsors&logoColor=white)](https://github.com/sponsors/hbakri)
[![Buy me a coffee](https://img.shields.io/badge/buy_me_a_coffee-donate-pink?logo=buy-me-a-coffee&logoColor=white)](https://www.buymeacoffee.com/hbakri)

Your kindness and support make a world of difference. Thank you! 🙏
