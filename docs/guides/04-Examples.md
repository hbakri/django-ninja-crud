# ✨ How It Works

Let's walk through a practical example of using Django Ninja CRUD to create a complete API for a university department system. This example will demonstrate how to set up models, schemas, and views with minimal code.

## 1. Define Your Model

First, we define a simple `Department` model:
```python
# examples/models.py
from django.db import models

class Department(models.Model):
    title = models.CharField(max_length=255, unique=True)
```

## 2. Create Your Schemas

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

## 3. Set Up Your Views
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

## 4. Simplified Version with Defaults

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

## 5. Error Handling

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
