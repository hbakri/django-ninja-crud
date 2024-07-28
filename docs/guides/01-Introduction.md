**Django Ninja CRUD** is a [**declarative**](https://en.wikipedia.org/wiki/Declarative_programming)
framework that revolutionizes the way you build APIs with
[**Django Ninja**](https://github.com/vitalik/django-ninja). It empowers
developers to create highly customizable, reusable, and modular API views,
ranging from basic [**CRUD** _(**C**reate, **R**ead, **U**pdate, **D**elete)_](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete)
operations to complex custom endpoints, all with minimal boilerplate code.

Inspired by DRF's [**ModelViewSet**](https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset)
but evolving beyond its limitations, Django Ninja CRUD adopts a
[**composition-over-inheritance**](https://en.wikipedia.org/wiki/Composition_over_inheritance)
approach for true modularity.

# 🌞 Key Features
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

# 📝 Requirements

[![Python versions](https://img.shields.io/pypi/pyversions/django-ninja-crud.svg?color=306998&label=python&logo=python&logoColor=white)](https://github.com/python/cpython)
[![Django versions](https://img.shields.io/badge/4.2_%7C_5.0-blue?color=0C4B33&label=django&logo=django&logoColor=white)](https://github.com/django/django)
[![Django Ninja versions](https://img.shields.io/badge/1.0_%7C_1.1_%7C_1.2-blue?color=black&label=django-ninja&logo=fastapi&logoColor=white)](https://github.com/vitalik/django-ninja)

# ⚒️ Installation

```bash
pip install django-ninja-crud
```

# 💬 What's Next?

- **Quick Examples**: The section contains easy-to-understand examples of how to use the package and test its features. This will provide you with a practical understanding of how the package works.
- **Detailed Documentation**: For a more comprehensive understanding of Django Ninja CRUD, navigate to our detailed documentation. Here, you'll find in-depth explanations of the package's features and capabilities, as well as advanced usage examples.
- **Community**: Join our community for discussions, support, and updates related to Django Ninja CRUD. Share your experiences, learn from others, and contribute to improving the package.
