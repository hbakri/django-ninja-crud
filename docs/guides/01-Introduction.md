**Django Ninja CRUD** is a [**declarative**](https://en.wikipedia.org/wiki/Declarative_programming) framework that revolutionizes the way you build APIs with [**Django Ninja**](https://github.com/vitalik/django-ninja). It empowers developers to create highly customizable, reusable, and modular API views, ranging from basic [**CRUD** _(**C**reate, **R**ead, **U**pdate, **D**elete)_](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations to complex custom endpoints, all with minimal boilerplate code.

Inspired by DRF's [**ModelViewSet**](https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset) but evolving beyond its limitations, Django Ninja CRUD adopts a [**composition-over-inheritance**](https://en.wikipedia.org/wiki/Composition_over_inheritance) approach for true modularity.

# 🌞 Key Features
- **Declarative Views**: Easily extend `APIView` to create reusable components for repeated business logic. Define views by stating intent, with unrestricted function signatures supporting both sync and async implementations.

- **Flexible Built-in CRUD Views**: Pre-built, customizable `ListView`, `CreateView`, `ReadView`, `UpdateView`, and `DeleteView` views. Use as-is, customize, or use as blueprints for your own implementations. Supports any path parameters, pagination, filtering, decorators, and more.

- **Powerful Viewset Composition**: Use views independently or compose them into `APIViewSet` for grouped, related views sharing attributes. Design versatile APIs supporting multiple instances of the same view type—perfect for API versioning, or alternative representations.

- **Seamless Django Ninja Integration**: Enhance your existing Django Ninja project without changing its structure. Gradually adopt declarative views to clean up your codebase and boost development efficiency.

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
