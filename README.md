# Django Ninja CRUD
[![example workflow](https://github.com/hbakri/django-ninja-crud/actions/workflows/tests.yml/badge.svg)](https://github.com/hbakri/django-ninja-crud/actions)
[![Coverage](https://img.shields.io/codecov/c/github/hbakri/django-ninja-crud/main.svg?label=coverage&logo=codecov&logoColor=white)](https://codecov.io/gh/hbakri/django-ninja-crud)
[![PyPI version](https://img.shields.io/pypi/v/django-ninja-crud?color=g&logo=pypi&logoColor=white)](https://pypi.org/project/django-ninja-crud/)
[![Downloads](https://static.pepy.tech/badge/django-ninja-crud/month)](https://pepy.tech/project/django-ninja-crud)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

![Django Ninja CRUD](https://raw.githubusercontent.com/hbakri/django-ninja-crud/main/assets/images/django-ninja-crud-cover.png)

Django Ninja CRUD is a powerful tool designed to streamline the development of **CRUD** (**C**reate, **R**ead, **U**pdate, **D**elete) operations in Django applications using the [Django Ninja](https://django-ninja.rest-framework.com) framework. It is intended to help developers save significant time by eliminating the need to write repetitive code for each operation and even more on the associated tests.

Developing these features from scratch every time can be _time-consuming_ and _error-prone_. That's where Django Ninja CRUD comes in—it provides a set of predefined, customizable "blueprints" for these operations, allowing developers to set them up quickly and reliably. Instead of getting bogged down with the details of how these operations are performed, developers can focus on the unique, creative aspects of their applications.

## 🏄 Key Features

Django Ninja CRUD is a flexible, transparent, and configurable solution to a common challenge in web development.

- **Flexibility:** _Designed to adapt to your needs_. Whether you're creating, retrieving, updating, or deleting data, you can shape your operations as you see fit. It allows developers to either use the standard operations or to define their own, tailored to their specific requirements.
- **Transparency:** _What you see is what you get_. The operations you define are the operations you perform, making it easy to understand and follow the data flow. It encourages practices that make your code easy to read and maintain. Also, it allows for easy testing of the defined operations, ensuring that everything works as expected.
- **Configurability:** _Provides a high degree of customization_. You're not locked into a rigid structure; instead, you can adjust and fine-tune your operations to suit your project's unique needs. You can use the built-in tools to quickly set up standard operations, and if needed, you can customize them or even build your own from scratch.

By using this package, developers can write efficient and clear code, saving time and reducing potential errors. It's a tool that accommodates the developer's workflow, rather than forcing the developer to adapt to it.

## 📝 Requirements

![Python versions](https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11-blue)
![Django versions](https://img.shields.io/badge/django-3.2%20|%204.1%20|%204.2-blue)
![Django Ninja versions](https://img.shields.io/badge/django--ninja-0.21.0%20|%200.22.0-blue)

## 📈 Installation
```bash
pip install django-ninja-crud
```
For more information, see the [installation guide](https://github.com/hbakri/django-ninja-crud/wiki/02_installation).

## 👨‍🎨 Example
### Usage
Let's imagine you're building a system for a university and you have a model called `Department`. Each department in your university has a unique title.

```python
# models.py
from django.db import models

class Department(models.Model):
    title = models.CharField(max_length=255, unique=True)
```

To interact with this data, we need a way to convert it between Python objects and a format that's easy to read and write (like JSON). In Django Ninja, we do this with `Schema`:

```python
# schemas.py
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
# views.py
from ninja import Router
from django.http import HttpRequest
from ninja_crud.views import (
    CreateModelView,
    DeleteModelView,
    ListModelView,
    ModelViewSet,
    RetrieveModelView,
    UpdateModelView,
)
from example.models import Department
from example.schemas import DepartmentIn, DepartmentOut

router = Router()

class DepartmentViewSet(ModelViewSet):
    model_class = Department

    # AbstractModelView subclasses can be used as-is
    list = ListModelView(output_schema=DepartmentOut)
    create = CreateModelView(input_schema=DepartmentIn, output_schema=DepartmentOut)
    retrieve = RetrieveModelView(output_schema=DepartmentOut)
    update = UpdateModelView(input_schema=DepartmentIn, output_schema=DepartmentOut)
    delete = DeleteModelView()

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
# tests.py
from django.test import TestCase
from example.models import Department
from example.views.view_department import DepartmentViewSet
from ninja_crud.tests import (
    PathParameters,
    Payloads,
    TestCreateModelView,
    TestDeleteModelView,
    TestListModelView,
    TestModelViewSet,
    TestRetrieveModelView,
    TestUpdateModelView,
)


class TestDepartmentViewSet(TestModelViewSet, TestCase):
    model_view_set_class = DepartmentViewSet
    base_path = "api/departments"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.department_1 = Department.objects.create(title="department-1")
        cls.department_2 = Department.objects.create(title="department-2")

    def get_path_parameters(self):
        return PathParameters(ok={"id": self.department_1.id}, not_found={"id": 9999})

    payloads = Payloads(
        ok={"title": "new_title"},
        bad_request={"bad-title": 1},
        conflict={"title": "department-2"},
    )

    test_list = TestListModelView()
    test_create = TestCreateModelView(payloads=payloads)
    test_retrieve = TestRetrieveModelView(path_parameters=get_path_parameters)
    test_update = TestUpdateModelView(path_parameters=get_path_parameters, payloads=payloads)
    test_delete = TestDeleteModelView(path_parameters=get_path_parameters)
```
With this package, these tests can be written in a consistent, straightforward way, making it easier to ensure your views are working as expected.

In summary, this package simplifies the process of setting up and testing **CRUD** operations in Django Ninja, letting you focus on what makes your application unique. By providing a flexible, transparent, and configurable solution, this package is a powerful tool for accelerating web development.

## 📚 Documentation
For more information, see the [documentation](https://github.com/hbakri/django-ninja-crud/wiki).

> 📘 **Note:**
>
> With the launch of the `v0.3.0` release, we've made substantial enhancements to improve the developer experience while using this package. A myriad of new features has been introduced, and deep refactorings have taken place—primarily focusing on the views and the associated testing suite.
>
> Currently, the documentation for the views has been thoroughly updated to reflect these changes. I'm in the process of updating and expanding the documentation for the revamped testing suite. Your patience and understanding are deeply valued as I work towards delivering a more detailed and up-to-date documentation experience. Thank you for supporting this project and its continuous growth!

## 🫶 Support
First and foremost, thank you for taking the time to explore this project. If you find it valuable or promising, please give it a star! Your recognition not only motivates but also helps others discover the project.

![GitHub Repo stars](https://img.shields.io/github/stars/hbakri/django-ninja-crud?style=social)

If you've benefited from this project or appreciate the dedication behind it, consider showing further support. Whether it's the price of a coffee, a word of encouragement, or a sponsorship, every gesture adds fuel to the open-source fire, making it shine even brighter. ✨

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/hbakri)

Your kindness and support make a world of difference. Thank you!
