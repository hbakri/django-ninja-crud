# The Django Ninja CRUD Documentation

![Django Ninja CRUD](https://raw.githubusercontent.com/hbakri/django-ninja-crud/main/docs/assets/images/django-ninja-crud-cover.png)

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

## ✨ Key Features
- **Purely Declarative**: Define views and tests by declaring what you want, not how to do it.
- **Unmatched Modularity**: Tailor your viewsets with desired CRUD views, customize each view's behavior.
- **Easy to Extend**: Create your own custom views and use them alongside the provided CRUD views as reusable components.
- **Scenario-based Testing Framework**: Leverage a scenario-based testing framework for defining diverse test cases declaratively and concisely.
- **Focus on What Matters**: Spend more time solving real-world problems and less on common and repetitive tasks.

> **Django Ninja CRUD is not just a tool; it's a paradigm shift in Django web application development and testing.**

## 🫶 Support
First and foremost, a heartfelt thank you to the 400+ stargazers who have shown their support for this project. Your recognition and belief in its potential fuel my drive to maintain and improve this work, making it more visible to new potential users and contributors.

[![Star History Chart](https://api.star-history.com/svg?repos=hbakri/django-ninja-crud&type=Date)](https://star-history.com/#hbakri/django-ninja-crud&Date)

If you've benefited from this project or appreciate the dedication behind it, consider showing further support. Whether it's the price of a coffee, a word of encouragement, or a sponsorship, every gesture adds fuel to the open-source fire, making it shine even brighter. ✨

[![Sponsor](https://img.shields.io/badge/sponsor-donate-pink?logo=github-sponsors&logoColor=white)](https://github.com/sponsors/hbakri)
[![Buy me a coffee](https://img.shields.io/badge/buy_me_a_coffee-donate-pink?logo=buy-me-a-coffee&logoColor=white)](https://www.buymeacoffee.com/hbakri)

Your kindness and support make a world of difference. Thank you! 🙏
