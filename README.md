# Django Ninja CRUD
[![example workflow](https://github.com/hbakri/django-ninja-crud/actions/workflows/tests.yml/badge.svg)](https://github.com/hbakri/django-ninja-crud/actions)
[![Coverage](https://img.shields.io/codecov/c/github/hbakri/django-ninja-crud/main.svg?label=coverage)](https://codecov.io/gh/hbakri/django-ninja-crud)
[![PyPI version](https://badge.fury.io/py/django-ninja-crud.svg)](https://badge.fury.io/py/django-ninja-crud)
[![Downloads](https://pepy.tech/badge/django-ninja-crud)](https://pepy.tech/project/django-ninja-crud)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Django Ninja CRUD](https://media.discordapp.net/attachments/1093869226202234930/1117550925083590677/Hicham_B._Django-ninja_cover_ce78724c-1512-41e5-86de-3ffa2cfd0ea9.png?width=2688&height=1070)

Django Ninja CRUD is a library that provides a set of generic views to perform **CRUD** operations (**C**reate, **R**etrieve, **U**pdate, **D**elete) on Django models using [Django Ninja](https://django-ninja.rest-framework.com/).

Features:
- **DRY**: No need to write the same code over and over again.
- **Customizable**: You can customize the views to fit your needs, or even write your own views.
- **Testable**: You can test your views easily, the same way you defined them.

## Installation
```bash
pip install django-ninja-crud
```

## Usage
Let's say you have a model called `Department`:
```python
# models.py
from django.db import models

class Department(models.Model):
    title = models.CharField(max_length=255, unique=True)
```

And you have a schema for serializing and deserializing the model:
```python
# schemas.py
from ninja import Schema

class DepartmentIn(Schema):
    title: str

class DepartmentOut(Schema):
    id: int
    title: str
```

Here is a brief example of how to use django-ninja-crud:

```python
# views.py
from example.models import Department
from example.schemas import DepartmentIn, DepartmentOut
from ninja import Router
from ninja_crud.views import ModelViewSet, ListModelView, CreateModelView,
    RetrieveModelView, UpdateModelView, DeleteModelView


class DepartmentViewSet(ModelViewSet):
    model = Department
    input_schema = DepartmentIn
    output_schema = DepartmentOut

    list = ListModelView(output_schema=output_schema)
    create = CreateModelView(input_schema=input_schema, output_schema=output_schema)
    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(input_schema=input_schema, output_schema=output_schema)
    delete = DeleteModelView()


router = Router()
DepartmentViewSet.register_routes(router)
```

## Testing
You can then write the associated tests like so:

```python
# tests.py
from django.test import TestCase
from example.models import Department
from example.views.view_department import DepartmentViewSet
from ninja_crud.tests import CreateModelViewTest, DeleteModelViewTest,
    ListModelViewTest, ModelViewSetTest, Payloads, RetrieveModelViewTest,
    UpdateModelViewTest


class DepartmentViewSetTest(ModelViewSetTest, TestCase):
    model_view_set = DepartmentViewSet

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.department_1 = Department.objects.create(title="department-1")
        cls.department_2 = Department.objects.create(title="department-2")

    def get_instance(self):
        return self.department_1

    department_payloads = Payloads(
        ok={"title": "department-updated"},
        bad_request={"bad-key": "department-updated"},
        conflict={"title": "department-2"},
    )

    test_list = ListModelViewTest(instance_getter=get_instance)
    test_create = CreateModelViewTest(payloads=department_payloads, instance_getter=get_instance)
    test_retrieve = RetrieveModelViewTest(instance_getter=get_instance)
    test_update = UpdateModelViewTest(payloads=department_payloads, instance_getter=get_instance)
    test_delete = DeleteModelViewTest(instance_getter=get_instance)
```

## Support
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/hbakri)
