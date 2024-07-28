# Django Ninja CRUD
[![Tests](https://github.com/hbakri/django-ninja-crud/actions/workflows/tests.yml/badge.svg)](https://github.com/hbakri/django-ninja-crud/actions)
[![Coverage](https://img.shields.io/codecov/c/github/hbakri/django-ninja-crud/main.svg?label=coverage&logo=codecov&logoColor=white)](https://codecov.io/gh/hbakri/django-ninja-crud)
[![PyPI version](https://img.shields.io/pypi/v/django-ninja-crud?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/django-ninja-crud/)
[![Downloads](https://static.pepy.tech/badge/django-ninja-crud/month)](https://pepy.tech/project/django-ninja-crud)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![MyPy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://github.com/python/mypy)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

![Django Ninja CRUD](https://raw.githubusercontent.com/hbakri/django-ninja-crud/main/docs/assets/images/django-ninja-crud-cover.png)

**Django Ninja CRUD** is a [**declarative**](https://en.wikipedia.org/wiki/Declarative_programming)
framework that revolutionizes the way you build APIs with
[**Django Ninja**](https://github.com/vitalik/django-ninja). It empowers
developers to create highly customizable, reusable, and modular API views,
ranging from basic **CRUD** ([**C**reate, **R**ead, **U**pdate, **D**elete](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete))
operations to complex custom endpoints, all with minimal boilerplate code.

Inspired by DRF's [ModelViewSet](https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset)
but evolving beyond its limitations, Django Ninja CRUD adopts a
[composition-over-inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance)
approach for true modularity.

## 🌞 Key Features
- **Declarative API Development**: Define views by stating intent, not implementation.
- **Composition Over Inheritance**: Build viewsets by composing modular, reusable views.
- **Flexible CRUD Views**: Pre-built, customizable List, Create, Read, Update, Delete views.
- **Custom View Creation**: Easily extend `APIView` for bespoke business logic.
- **Standalone or Viewset Integration**: Use views independently or within `APIViewSet` to group related views.
- **Viewset Attributes Inheritance**: `APIView` subclasses can access `APIViewSet` attributes, allowing for centralized configuration.
- **Multiple View Instances**: Support for versioning and alternative representations by allowing multiple instances of the same view type within a viewset.
- **Unrestricted Handler Signatures**: Implement `handler` method in custom views with any function signature, supporting all request components.
- **Optional Path Parameters Type Annotations**: Infer path parameters from view's `path` and `model` attributes, reducing redundancy.
- **Flexible Authentication & Permissions**: Apply custom checks via decorators or within views.
- **Efficient Codebase**: Powerful functionality in a compact, well-crafted package with ~300 lines of code.

> [!NOTE]
> As I shared in my [DjangoCON Europe 2024 talk](https://www.youtube.com/watch?v=r8yRxZPcy9k&t=1168s),
> Django Ninja CRUD emerged from countless hours of wrestling with repetitive code.
> It's driven by a vision to make Django API development not just more efficient,
> but truly intuitive and enjoyable. I hope it revolutionizes your development
> experience as profoundly as it has mine.

## 📝 Requirements

[![Python versions](https://img.shields.io/pypi/pyversions/django-ninja-crud.svg?color=306998&label=python&logo=python&logoColor=white)](https://github.com/python/cpython)
[![Django versions](https://img.shields.io/badge/4.2_%7C_5.0-blue?color=0C4B33&label=django&logo=django&logoColor=white)](https://github.com/django/django)
[![Django Ninja versions](https://img.shields.io/badge/1.0_%7C_1.1_%7C_1.2-blue?color=black&label=django-ninja&logo=fastapi&logoColor=white)](https://github.com/vitalik/django-ninja)

## ⚒️ Installation
```bash
pip install django-ninja-crud
```
For more information, see the [installation guide](https://django-ninja-crud.readme.io/docs/02-installation).

## ✨ How It Works

Let's walk through a practical example of using Django Ninja CRUD to create a complete API for a university department system. This example will demonstrate how to set up models, schemas, and views with minimal code.

### 1. Define Your Model

First, we define a simple `Department` model:
```python
# examples/models.py
from django.db import models

class Department(models.Model):
    title = models.CharField(max_length=255, unique=True)
```

### 2. Create Your Schemas

Next, we define schemas for input and output:
```python
# examples/schemas.py
from ninja import Schema

# For creating/updating departments
class DepartmentIn(Schema):
    title: str

# For retrieving department data
class DepartmentOut(Schema):
    id: int
    title: str
```

### 3. Set Up Your Views
Now, here's where Django Ninja CRUD shines. Set up all CRUD operations in one concise class:

```python
# examples/views/department_views.py
from typing import List

from ninja import NinjaAPI
from ninja_crud import views, viewsets

from examples.models import Department
from examples.schemas import DepartmentIn, DepartmentOut

api = NinjaAPI()

class DepartmentViewSet(viewsets.APIViewSet):
    api = api
    model = Department

    # Define all CRUD operations with minimal code
    list_departments = views.ListView(response_body=List[DepartmentOut])
    create_department = views.CreateView(request_body=DepartmentIn, response_body=DepartmentOut)
    read_department = views.ReadView(response_body=DepartmentOut)
    update_department = views.UpdateView(request_body=DepartmentIn, response_body=DepartmentOut)
    delete_department = views.DeleteView()

# You can still add custom endpoints as needed using pure Django Ninja syntax
@api.get("/stats/")
def get_department_stats(request):
    return {"total": Department.objects.count()}
```

This code automatically creates the following API endpoints:
- GET `/` - List all departments with pagination limit/offset
- POST `/` - Create a new department
- GET `/{id}` - Retrieve a specific department
- PUT `/{id}` - Update a specific department
- DELETE `/{id}` - Delete a specific department
- GET `/stats/` - Custom endpoint for department statistics

### 4. Simplified Version with Defaults

For even more concise code, if your views are straightforward, you can leverage the
`APIViewSet` class to define them with default request and response bodies:
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

    # Extremely concise CRUD definitions
    list_departments = views.ListView()
    create_department = views.CreateView()
    read_department = views.ReadView()
    update_department = views.UpdateView()
    delete_department = views.DeleteView()
```

This produces the same API endpoints as the previous example, but with even less code.

### 5. Error Handling

> [!WARNING]
> Django Ninja CRUD's provided CRUD endpoints **DO NOT** include built-in error handling.
> This design choice allows you to maintain full control over error responses and
> adhere to your application's specific conventions.

To properly handle exceptions such as `ObjectDoesNotExist`, validation errors, or any
other potential issues, you need to define custom exception handlers as specified in
the [Django Ninja documentation](https://django-ninja.dev/guides/errors/).

For example, to handle `ObjectDoesNotExist` exceptions, you might add the following to
your code:
```python
from django.core.exceptions import ObjectDoesNotExist
from ninja import NinjaAPI

api = NinjaAPI()

@api.exception_handler(ObjectDoesNotExist)
def handle_object_does_not_exist(request, exc):
    return api.create_response(
        request,
        {"message": "Object not found"},
        status=404,
    )
```

## ☔️ Testing

Django Ninja CRUD is designed to work seamlessly with Django's testing framework and
other third-party testing tools. Users are encouraged to implement thorough tests for
their APIs using their preferred testing methodologies.

> [!NOTE]
> Previously, Django Ninja CRUD included built-in testing utilities. These have been
> separated into a standalone project, [django-rest-testing](https://github.com/hbakri/django-rest-testing),
> to allow for broader use cases beyond Django Ninja. While it offers a declarative,
> scenario-based approach to API testing, it's still in active development. The project
> aims to improve its functionality and developer experience over time. Users are
> advised to evaluate it alongside other testing methods to find the best fit for
> their projects.

While **Django Rest Testing** is used in Django Ninja CRUD's own test suite, it is not a
runtime dependency. Users are free to choose the testing approach that best suits their
needs without any limitations imposed by the main package.

## 📚 Documentation
For more information, see the [documentation](https://django-ninja-crud.readme.io/).

## 🫶 Support
First and foremost, a heartfelt thank you to the 400+ stargazers who have shown their
support for this project!

[![Star History Chart](https://api.star-history.com/svg?repos=hbakri/django-ninja-crud&type=Date)](https://star-history.com/#hbakri/django-ninja-crud&Date)

As an open-source project, Django Ninja CRUD thrives on community contributions and
support. Here are some ways you can help:

- 🌟 Star the repo
- 🙌 Share your experience
- 🐝 Report issues
- 🔥 Contribute code
- 💕 [Sponsor the project](https://github.com/sponsors/hbakri)

Your support, in any form, propels this project forward and helps it reach more
developers in need of a powerful, intuitive API development framework. Thank you! 🙏
