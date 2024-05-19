Django Ninja CRUD is a powerful, [declarative](https://en.wikipedia.org/wiki/Declarative_programming), and yet a little bit opinionated framework that
simplifies the development of **CRUD** ([**C**reate, **R**ead, **U**pdate, **D**elete](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete))
endpoints with [Django Ninja](https://github.com/vitalik/django-ninja), and also
provides a declarative scenario-based way for testing these endpoints with
[Django REST Testing](https://github.com/hbakri/django-rest-testing) _(the little brother of this package)_ 🐣.
It allows you to define common endpoints as class-based views and customize them to
conform to your project's conventions with ease, and also create easily your own
custom views and declare them alongside the provided CRUD views, fostering modularity
and extensibility. This package promotes focusing on what matters most:
**solving real problems**, not reinventing the wheel all over your project.

Initially inspired by DRF's [ModelViewSet](https://www.django-rest-framework.org/api-guide/viewsets/#modelviewset),
Django Ninja CRUD evolved to address its limitations, adopting a
[composition-over-inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance)
approach to achieve true modularity – a foundational step towards a broader declarative
interface for endpoint creation.

Key challenges with inheritance-based viewsets:
- **Unicity of CRUD endpoints per model**: Django Ninja CRUD allows you to define multiple endpoints for the same model, enabling versioning or alternative representations.
- **Customization inflexibility**: Instead of overriding methods on a monolithic class, you can customize individual views through composition and configuration.
- **Implicit relations within inheritance hierarchies**: Composition decouples views, reducing dependencies and promoting reusability.
- **Lack of modularity for new endpoints**: Adding custom endpoints no longer requires subclassing the entire viewset, making it easier to introduce new functionality incrementally.

# ✨ Key Features
- **Purely Declarative**: Define views and tests by declaring what you want, not how to do it.
- **Unmatched Modularity**: Tailor your viewsets with desired CRUD views, customize each view's behavior.
- **Easy to Extend**: Create your own custom views and use them alongside the provided CRUD views as reusable components.
- **Scenario-based Testing Framework**: Leverage a scenario-based testing framework for defining diverse test cases declaratively and concisely.
- **Focus on What Matters**: Spend more time solving real-world problems and less on common and repetitive tasks.

> **Django Ninja CRUD is not just a tool; it's a paradigm shift in Django web application development and testing.**

# 📝 Requirements

[![Python versions](https://img.shields.io/pypi/pyversions/django-ninja-crud.svg?color=306998&label=python&logo=python&logoColor=white)](https://github.com/python/cpython)
[![Django versions](https://img.shields.io/badge/3.2_|_4.1_|_4.2_|_5.0-blue?color=0C4B33&label=django&logo=django&logoColor=white)](https://github.com/django/django)
[![Django Ninja versions](https://img.shields.io/badge/1.0_|_1.1-blue?color=black&label=django-ninja&logo=fastapi&logoColor=white)](https://github.com/vitalik/django-ninja)

# ⚒️ Installation

```shell
pip install django-ninja-crud[testing]
```

# 💬 What's Next?

- **Quick Examples**: The section contains easy-to-understand examples of how to use the package and test its features. This will provide you with a practical understanding of how the package works.
- **Detailed Documentation**: For a more comprehensive understanding of Django Ninja CRUD, navigate to our detailed documentation. Here, you'll find in-depth explanations of the package's features and capabilities, as well as advanced usage examples.
- **Community**: Join our community for discussions, support, and updates related to Django Ninja CRUD. Share your experiences, learn from others, and contribute to improving the package.
