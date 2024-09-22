**Django Ninja CRUD** introduces [**modularity**](https://en.wikipedia.org/wiki/Modular_programming) to API development with [**Django Ninja**](https://github.com/vitalik/django-ninja), revolutionizing how APIs are built and maintained at scale while avoiding repetition. It empowers developers to create reusable, [**composable**](https://en.wikipedia.org/wiki/Composability) API views ranging from built-in [**CRUD** (**C**reate, **R**ead, **U**pdate, **D**elete)](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations to complex custom endpoints, supporting both sync and async implementations, all with minimal boilerplate code.

# 🌞 Key Features
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

# 📝 Requirements

[![Python versions](https://img.shields.io/pypi/pyversions/django-ninja-crud.svg?color=306998&label=python&logo=python&logoColor=white)](https://github.com/python/cpython)
[![Django versions](https://img.shields.io/badge/4.2_%7C_5.0_%7C_5.1-blue?color=0C4B33&label=django&logo=django&logoColor=white)](https://github.com/django/django)
[![Django Ninja versions](https://img.shields.io/badge/1.0_%7C_1.1_%7C_1.2_%7C_1.3-blue?color=black&label=django-ninja&logo=fastapi&logoColor=white)](https://github.com/vitalik/django-ninja)

# ⚒️ Installation

```bash
pip install django-ninja-crud
```

# 💬 What's Next?

- **Quick Examples**: The section contains easy-to-understand examples of how to use the package and test its features. This will provide you with a practical understanding of how the package works.
- **Detailed Documentation**: For a more comprehensive understanding of Django Ninja CRUD, navigate to our detailed documentation. Here, you'll find in-depth explanations of the package's features and capabilities, as well as advanced usage examples.
- **Community**: Join our community for discussions, support, and updates related to Django Ninja CRUD. Share your experiences, learn from others, and contribute to improving the package.
