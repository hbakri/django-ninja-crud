# Django Ninja CRUD
[![PyPI version](https://badge.fury.io/py/django-ninja-crud.svg?)](https://badge.fury.io/py/django-ninja-crud)
[![codecov](https://codecov.io/gh/hbakri/django-ninja-crud/branch/main/graph/badge.svg?token=G18HY2POF8)](https://codecov.io/gh/hbakri/django-ninja-crud)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/django-ninja-crud/month)](https://pepy.tech/project/django-ninja-crud)

[//]: # (Add image under this line)
![Django Ninja CRUD](https://media.discordapp.net/attachments/1093869226202234930/1117550925083590677/Hicham_B._Django-ninja_cover_ce78724c-1512-41e5-86de-3ffa2cfd0ea9.png?width=2688&height=1070)

Django Ninja CRUD is a library that provides a set of generic views to perform CRUD operations on Django models using [Django Ninja](https://django-ninja.rest-framework.com/).

## Installation
```bash
pip install django-ninja-crud
```

## Usage
```python
from ninja_crud.views import ModelViewSet, ListModelView, CreateModelView, \
    RetrieveModelView, UpdateModelView, DeleteModelView
from examples.models import Department
from examples.schemas import DepartmentIn, DepartmentOut


class DepartmentViewSet(ModelViewSet):
    model = Department
    input_schema = DepartmentIn
    output_schema = DepartmentOut

    list = ListModelView(output_schema=output_schema)
    create = CreateModelView(input_schema=input_schema, output_schema=output_schema)
    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(input_schema=input_schema, output_schema=output_schema)
    delete = DeleteModelView()
```

## Support
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/hbakri)
