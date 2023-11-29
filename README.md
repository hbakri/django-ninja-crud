# Django Ninja CRUD
[![Tests](https://github.com/hbakri/django-ninja-crud/actions/workflows/tests.yml/badge.svg)](https://github.com/hbakri/django-ninja-crud/actions)
[![Coverage](https://img.shields.io/codecov/c/github/hbakri/django-ninja-crud/main.svg?label=coverage&logo=codecov&logoColor=white)](https://codecov.io/gh/hbakri/django-ninja-crud)
[![PyPI version](https://img.shields.io/pypi/v/django-ninja-crud?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/django-ninja-crud/)
[![Downloads](https://static.pepy.tech/badge/django-ninja-crud/month)](https://pepy.tech/project/django-ninja-crud)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

![Django Ninja CRUD](https://raw.githubusercontent.com/hbakri/django-ninja-crud/main/docs/assets/images/django-ninja-crud-cover.png)

Django Ninja CRUD is a [declarative](https://en.wikipedia.org/wiki/Declarative_programming), powerful, and yet opinionated framework that simplifies the development of **CRUD** ([**C**reate, **R**ead, **U**pdate, **D**elete](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete)) views and tests with [Django Ninja](https://github.com/vitalik/django-ninja).
It promotes best practices for efficient, robust endpoint creation, allowing you to focus on what matters most: solving real problems.
Initially inspired by DRF's [ModelViewSet](https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset), Django Ninja CRUD evolved to address its limitations, adopting a [composition-over-inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance) approach to achieve true modularity – a foundational step towards a broader declarative interface for endpoint creation.

## ✨ Key Features
- **Purely Declarative**: Embrace an approach where defining views and tests is a matter of declaring what you want, not how to achieve it.
- **Unmatched Modularity**: Tailor your viewsets with the desired CRUD views and customize each view's behavior with ease. Extend the flexibility by creating your own subclasses of the provided views and tests.
- **Powerful Testing Framework**: Leverage a matrix-based testing framework for defining diverse test scenarios declaratively.
- **Focus on What Matters**: Spend more time solving real-world problems and less on CRUD boilerplate.

Its blend of declarative syntax, modularity, and powerful testing capabilities sets a new standard for developers seeking efficiency and precision.

> **Django Ninja CRUD is not just a tool; it's a paradigm shift in Django web application development and testing.**

## 📝 Requirements

![Python versions](https://img.shields.io/pypi/pyversions/django-ninja-crud.svg?color=306998&label=python&logo=python&logoColor=white)
![Django versions](https://img.shields.io/badge/3.2%20|%204.1%20|%204.2%20|%205.0b1-blue?color=0C4B33&label=django&logo=django&logoColor=white)
![Django Ninja versions](https://img.shields.io/badge/0.21%20|%200.22%20|%201.0-blue?color=black&label=django-ninja&logo=fastapi&logoColor=white)

## ⚒️ Installation
```bash
pip install django-ninja-crud
```
For more information, see the [installation guide](https://django-ninja-crud.readme.io/docs/02-installation).

## 👨‍🎨 Example
### Usage
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

Now, here comes the power of Django Ninja CRUD. With it, you can set up the **CRUD** operations for the `Department` model with just a few lines of code:

```python
# examples/views/department_views.py
from django.http import HttpRequest
from ninja import Router
from ninja_crud import views, viewsets

from examples.models import Department
from examples.schemas import DepartmentIn, DepartmentOut

router = Router()


class DepartmentViewSet(viewsets.ModelViewSet):
    model = Department
    default_input_schema = DepartmentIn
    default_output_schema = DepartmentOut

    list_view = views.ListModelView()
    create_view = views.CreateModelView()
    retrieve_view = views.RetrieveModelView()
    update_view = views.UpdateModelView()
    delete_view = views.DeleteModelView()


# The register_routes method must be called to register the routes
DepartmentViewSet.register_routes(router)


# Beyond the CRUD operations managed by the viewset,
# the router can be used in the standard Django Ninja way
@router.get("/statistics/", response=dict)
def retrieve_department_statistics(request: HttpRequest):
    return {"total": Department.objects.count()}
```

### Testing
A key advantage of this package is that it makes your views easy to test. Once you've set up your **CRUD** operations, you can write tests to ensure they're working as expected. Here's an example of how you might test the `Department` operations:

```python
# examples/tests/test_department_views.py
from ninja_crud import testing

from examples.models import Department
from examples.views.department_views import DepartmentViewSet


class TestDepartmentViewSet(testing.viewsets.ModelViewSetTestCase):
    model_viewset_class = DepartmentViewSet
    base_path = "api/departments"

    @classmethod
    def setUpTestData(cls):
        cls.department_1 = Department.objects.create(title="department-1")
        cls.department_2 = Department.objects.create(title="department-2")

    @property
    def path_parameters(self):
        return testing.components.PathParameters(
            ok={"id": self.department_1.id},
            not_found={"id": 9999}
        )

    @property
    def payloads(self):
        return testing.components.Payloads(
            ok={"title": "department-3"},
            bad_request={},
            conflict={"title": self.department_2.title},
        )

    test_list_view = testing.views.ListModelViewTest()
    test_create_view = testing.views.CreateModelViewTest(payloads)
    test_retrieve_view = testing.views.RetrieveModelViewTest(path_parameters)
    test_update_view = testing.views.UpdateModelViewTest(path_parameters, payloads)
    test_delete_view = testing.views.DeleteModelViewTest(path_parameters)

    # You can then add additional tests as needed
    def test_retrieve_department_statistics(self):
        response = self.client.get(f"{self.base_path}/statistics/")
        self.assertEqual(response.status_code, 200)
        ... # Additional assertions
```

## 📚 Documentation
For more information, see the [documentation](https://django-ninja-crud.readme.io/).

## 🫶 Support
First and foremost, a heartfelt thank you for taking an interest in this project. If it has been helpful to you or you believe in its potential, kindly consider giving it a star on GitHub. Such recognition not only fuels my drive to maintain and improve this work but also makes it more visible to new potential users and contributors.

![GitHub Repo stars](https://img.shields.io/github/stars/hbakri/django-ninja-crud?style=social)

If you've benefited from this project or appreciate the dedication behind it, consider showing further support. Whether it's the price of a coffee, a word of encouragement, or a sponsorship, every gesture adds fuel to the open-source fire, making it shine even brighter. ✨

[![Sponsor](https://img.shields.io/badge/sponsor-donate-pink?logo=github-sponsors&logoColor=white)](https://github.com/sponsors/hbakri)
[![Buy me a coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-pink?logo=buy-me-a-coffee&logoColor=white)](https://www.buymeacoffee.com/hbakri)

Your kindness and support make a world of difference. Thank you! 🙏
