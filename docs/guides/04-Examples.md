In this section, we'll walk through some quick examples of how to use Django Ninja CRUD. The goal is to illustrate how simple it is to define data operations and tests with this tool.

# 👨‍🎨 Usage
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
    default_payload_schema = DepartmentIn
    default_response_schema = DepartmentOut

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

# 🥷 Testing
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
With this package, these tests can be written in a consistent, straightforward way, making it easier to ensure your views are working as expected.
