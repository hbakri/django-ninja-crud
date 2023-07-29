In this section, we'll walk through some quick examples of how to use Django Ninja CRUD. The goal is to illustrate how simple it is to define data operations and tests with this tool.

# 👨‍🎨 Usage

Let's imagine you're building a system for a university and you have a model called `Department`. Each department in your university has a unique `title`.

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
from example.models import Department
from example.schemas import DepartmentIn, DepartmentOut
from ninja import Router
from ninja_crud.views import ModelViewSet, ListModelView, CreateModelView, \
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

This piece of code sets up a system where you can list all departments, create a new department, retrieve the details of a specific department, update a department, and delete a department. And all of this with just a simple class declaration!

# 🥷 Testing

A key advantage of Django Ninja CRUD is that it makes your views easy to test. Once you've set up your **CRUD** operations, you can write tests to ensure they're working as expected. Here's an example of how you might test the `Department` operations:

```python
# tests.py
from django.test import TestCase
from example.models import Department
from example.views.view_department import DepartmentViewSet
from ninja_crud.tests import CreateModelViewTest, DeleteModelViewTest, \
    ListModelViewTest, ModelViewSetTest, RetrieveModelViewTest, UpdateModelViewTest, \
    BodyParams, PathParams


class DepartmentViewSetTest(ModelViewSetTest, TestCase):
    model_view_set = DepartmentViewSet

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.department_1 = Department.objects.create(title="department-1")
        cls.department_2 = Department.objects.create(title="department-2")

    def get_path_params(self):
        return PathParams(ok={"id": self.department_1.id}, not_found={"id": 9999})

    body_params = BodyParams(
        ok={"title": "new_title"},
        bad_request={"bad-title": 1},
        conflict={"title": "department-2"},
    )

    test_list = ListModelViewTest()
    test_create = CreateModelViewTest(body_params=body_params)
    test_retrieve = RetrieveModelViewTest(path_params=get_path_params)
    test_update = UpdateModelViewTest(path_params=get_path_params, body_params=body_params)
    test_delete = DeleteModelViewTest(path_params=get_path_params)
```

In this test code, we first set up some sample data to work with: two departments with different titles. We then define a suite of tests to check each of our **CRUD** operations: listing departments, creating a new department, retrieving a department, updating a department, and deleting a department.

Each test uses the id of an instance of the Department model (retrieved with the `get_path_params` method) and a set of `body_params` representing different scenarios (e.g., a successful update, an update with an incorrect key, and an update that would cause a conflict).

With this package, these tests can be written in a consistent, straightforward way, making it easier to ensure your views are working as expected. Once you've written these tests, you can run them whenever you make changes to your views, giving you confidence that your changes haven't broken anything.

In summary, Django Ninja CRUD simplifies the process of setting up and testing CRUD operations in Django Ninja, letting you focus on what makes your application unique. By providing a **flexible**, **transparent**, and **configurable** solution, Django Ninja CRUD is a powerful tool for accelerating web development.
