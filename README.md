# Django Ninja CRUD
[![Tests](https://github.com/hbakri/django-ninja-crud/actions/workflows/tests.yml/badge.svg)](https://github.com/hbakri/django-ninja-crud/actions)
[![Coverage](https://img.shields.io/codecov/c/github/hbakri/django-ninja-crud/main.svg?label=coverage&logo=codecov&logoColor=white)](https://codecov.io/gh/hbakri/django-ninja-crud)
[![PyPI Version](https://img.shields.io/pypi/v/django-ninja-crud?color=g&logo=pypi&logoColor=white)](https://pypi.org/project/django-ninja-crud/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/django-ninja-crud?logo=esri&logoColor=white)](https://pypistats.org/packages/django-ninja-crud)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/hbakri/django-ninja-crud/blob/main/LICENSE)
[![MyPy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://github.com/python/mypy)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

![Django Ninja CRUD Cover](https://raw.githubusercontent.com/hbakri/django-ninja-crud/main/docs/assets/images/django-ninja-crud-cover.JPG)

**Django Ninja CRUD** introduces [**modularity**](https://en.wikipedia.org/wiki/Modular_programming) to API development with [**Django Ninja**](https://github.com/vitalik/django-ninja), revolutionizing how APIs are built and maintained at scale while avoiding repetition. It empowers developers to create reusable, [**composable**](https://en.wikipedia.org/wiki/Composability) API views ranging from built-in [**CRUD** (**C**reate, **R**ead, **U**pdate, **D**elete)](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations to complex custom endpoints, supporting both sync and async implementations, all with minimal boilerplate code.

## 🌞 Key Features
- **Modular Views**: Easily extend `APIView` to create reusable components for repeated business logic. Define views by stating intent, with unrestricted function signatures supporting both sync and async implementations.

- **Flexible Built-in CRUD Views**: Pre-built, customizable `ListView`, `CreateView`, `ReadView`, `UpdateView`, and `DeleteView` views. Use as-is, customize, or use as blueprints for your own implementations. Supports any path parameters, pagination, filtering, decorators, and more.

- **Powerful Viewset Composition**: Use views independently or compose them into `APIViewSet` for grouped, related views sharing attributes. Design versatile APIs supporting multiple instances of the same view type—perfect for API versioning, or alternative representations.

- **Seamless Django Ninja Integration**: Enhance your existing Django Ninja project without changing its structure. Gradually adopt declarative views to clean up your codebase and boost development efficiency.

![Django Ninja CRUD Code](https://raw.githubusercontent.com/hbakri/django-ninja-crud/main/docs/assets/images/django-ninja-crud-code.JPG)

> [!NOTE]
> As shared in my [DjangoCON Europe 2024 talk](https://www.youtube.com/watch?v=r8yRxZPcy9k&t=1168s),
> Django Ninja CRUD emerged from countless hours of wrestling with repetitive, complex
> and hard-to-maintain APIs. My vision is to address those common pain points by
> providing a declarative and modular approach, making API development not just more
> efficient, but truly intuitive and enjoyable. I hope it revolutionizes your
> development experience as it has mine.

## 📝 Requirements

[![Python versions](https://img.shields.io/pypi/pyversions/django-ninja-crud.svg?color=306998&label=python&logo=python&logoColor=white)](https://github.com/python/cpython)
[![Django versions](https://img.shields.io/badge/4.2_%7C_5.0_%7C_5.1-blue?color=0C4B33&label=django&logo=django&logoColor=white)](https://github.com/django/django)
[![Django Ninja versions](https://img.shields.io/badge/1.0_%7C_1.1_%7C_1.2_%7C_1.3-blue?color=black&label=django-ninja&logo=fastapi&logoColor=white)](https://github.com/vitalik/django-ninja)

## ⚒️ Installation
```bash
pip install django-ninja-crud
```
For more information, see the [installation guide](https://django-ninja-crud.readme.io/docs/02-installation).

## ✨ How to Use Built-in CRUD Views

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

## 🌎 International Documentation

- [Chinese Documentation](https://django-ninja.cn/django-ninja-crud/) (Community Contributed)

> [!WARNING]
> Community-contributed translations may not always reflect the latest updates.

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
