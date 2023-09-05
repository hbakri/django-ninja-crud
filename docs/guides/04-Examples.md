In this section, we'll walk through some quick examples of how to use Django Ninja CRUD. The goal is to illustrate how simple it is to define data operations and tests with this tool.

# 👨‍🎨 Usage

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

# 🥷 Testing
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
