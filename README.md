# Django Ninja CRUD
[![Tests](https://github.com/hbakri/django-ninja-crud/actions/workflows/tests.yml/badge.svg)](https://github.com/hbakri/django-ninja-crud/actions)
[![Coverage](https://img.shields.io/codecov/c/github/hbakri/django-ninja-crud/main.svg?label=coverage&logo=codecov&logoColor=white)](https://codecov.io/gh/hbakri/django-ninja-crud)
[![PyPI version](https://img.shields.io/pypi/v/django-ninja-crud?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/django-ninja-crud/)
[![Downloads](https://static.pepy.tech/badge/django-ninja-crud/month)](https://pepy.tech/project/django-ninja-crud)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

![Django Ninja CRUD](https://raw.githubusercontent.com/hbakri/django-ninja-crud/main/docs/assets/images/django-ninja-crud-cover.png)

Django Ninja CRUD is an opinionated and powerful framework that accelerates the development of **CRUD** ([**C**reate, **R**ead, **U**pdate, **D**elete](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete)) operations with [Django Ninja](https://github.com/vitalik/django-ninja), promoting best practices for efficient, robust endpoint creation.
Equally significant is its integrated testing suite: a robust, user-friendly toolset ensuring that your endpoints are not only swiftly constructed but also meticulously tested and validated, reflecting a commitment to quality and reliability in your development workflow.

## ⚡️ Key Features

- **Streamlined Setup**: With just a few lines of code, your **CRUD** operations are ready to roll. No more copy-pasting or reinventing the wheel for each project.
- **Focus on What Matters**: Spend your precious time solving real problems, not stitching together basic operations. Django Ninja CRUD is like a trusty sidekick, handling the routine while you strategize the big picture.
- **Reliable Code**: Predefined blueprints are battle-tested and developer-approved. They're customizable, transparent, and designed with best practices in mind.
- **Integrated Testing Framework**: A robust, user-friendly toolset ensures that your endpoints are not only swiftly constructed but also meticulously tested and validated, reflecting a commitment to quality and reliability in your development workflow.

## 📝 Requirements

![Python versions](https://img.shields.io/pypi/pyversions/django-ninja-crud.svg?color=306998&label=python&logo=python&logoColor=white)
![Django versions](https://img.shields.io/pypi/frameworkversions/django/django-ninja-crud.svg?color=0C4B33&label=django&logo=django&logoColor=white)
![Django Ninja versions](https://img.shields.io/badge/0.21%20|%200.22%20|%201.0rc0-blue?color=black&label=django-ninja&logo=fastapi&logoColor=white)

## 📈 Installation
```bash
pip install django-ninja-crud
```
For more information, see the [installation guide](https://github.com/hbakri/django-ninja-crud/wiki/02_installation).

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


# The register_routes method must be called to register the routes with the router
DepartmentViewSet.register_routes(router)


# The router can then be used as normal
@router.get("/{name}", response=DepartmentOut)
def get_department_by_name(request: HttpRequest, name: str):
    return Department.objects.get(name=name)
```

### Testing
A key advantage of this package is that it makes your views easy to test. Once you've set up your **CRUD** operations, you can write tests to ensure they're working as expected. Here's an example of how you might test the `Department` operations:

```python
# examples/tests/test_department_views.py
from ninja_crud.testing.core.components import PathParameters, Payloads
from ninja_crud.testing.views import (
    CreateModelViewTest,
    DeleteModelViewTest,
    ListModelViewTest,
    RetrieveModelViewTest,
    UpdateModelViewTest,
)
from ninja_crud.testing.viewsets import ModelViewSetTestCase

from examples.models import Department
from examples.views.department_views import DepartmentViewSet


class TestDepartmentViewSet(ModelViewSetTestCase):
    model_viewset_class = DepartmentViewSet
    base_path = "api/departments"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.department_1 = Department.objects.create(title="department-1")
        cls.department_2 = Department.objects.create(title="department-2")

    def get_path_parameters(self):
        return PathParameters(ok={"id": self.department_1.id}, not_found={"id": 9999})

    payloads = Payloads(
        ok={"title": "department-3"},
        bad_request={"wrong_field": "wrong_value"},
        conflict={"title": "department-2"},
    )

    test_list_view = ListModelViewTest()
    test_create_view = CreateModelViewTest(payloads=payloads)
    test_retrieve_view = RetrieveModelViewTest(path_parameters=get_path_parameters)
    test_update_view = UpdateModelViewTest(path_parameters=get_path_parameters, payloads=payloads)
    test_delete_view = DeleteModelViewTest(path_parameters=get_path_parameters)

    # You can then add additional tests as needed
    def test_get_department_by_name(self):
        response = self.client.get(f"{self.base_path}/department-1")
        self.assertEqual(response.status_code, 200)
        ... # Additional assertions
```
With this package, these tests can be written in a consistent, straightforward way, making it easier to ensure your views are working as expected.

## 📚 Documentation
For more information, see the [documentation](https://github.com/hbakri/django-ninja-crud/wiki).

> [!NOTE]
>
> With the launch of the `v0.4.0` release, we've made substantial enhancements to improve the developer experience while using this package. A myriad of new features has been introduced, and deep refactorings have taken place—primarily focusing on the testing suite.
>
> Currently, the documentation for the views has been thoroughly updated to reflect these changes. I'm in the process of updating and expanding the documentation for the revamped testing suite. Your patience and understanding are deeply valued as I work towards delivering a more detailed and up-to-date documentation experience. Thank you for supporting this project and its continuous growth!

## 🫶 Support
First and foremost, a heartfelt thank you for taking an interest in this project. If it has been helpful to you or you believe in its potential, kindly consider giving it a star on GitHub. Such recognition not only fuels my drive to maintain and improve this work but also makes it more visible to new potential users and contributors.

![GitHub Repo stars](https://img.shields.io/github/stars/hbakri/django-ninja-crud?style=social)

If you've benefited from this project or appreciate the dedication behind it, consider showing further support. Whether it's the price of a coffee, a word of encouragement, or a sponsorship, every gesture adds fuel to the open-source fire, making it shine even brighter. ✨

[![Sponsor](https://img.shields.io/badge/sponsor-donate-pink?logo=github-sponsors&logoColor=white)](https://github.com/sponsors/hbakri)
[![Buy me a coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-pink?logo=buy-me-a-coffee&logoColor=white)](https://www.buymeacoffee.com/hbakri)

Your kindness and support make a world of difference. Thank you! 🙏
