Django Ninja CRUD is built around a series of core classes and views that form the heart of its functionality. Understanding these components is essential to effectively use the library and adapt it to your unique needs. This section provides a high-level overview of these core concepts. Each concept will be explored in-depth in their respective subpages.

# Key architectural choice

While this package was initially inspired by [Django REST Framework](https://www.django-rest-framework.org)'s `ModelViewSet`, it ultimately embraced a different paradigm, favoring **composition** over **inheritance**.

Inheritance in **O**bject-**O**riented **P**rogramming (**OOP**) allows new objects to take on existing properties. While efficient in some cases, it can lead to high coupling between classes and encourage a monolithic design, which can complicate code comprehension, maintenance, and evolution.

Conversely, the library employs composition, constructing classes by combining simpler components. This choice offers several advantages:

- **Flexibility**: Allows behavior changes at run-time, unlike inheritance where behavior is largely determined by the parent class.
- **Simplicity**: Components in a composition model are typically simpler due to fewer responsibilities, making them easier to understand, test, and debug.
- **Evolvability**: Facilitates system adaptation and extension through adding new parts or modifying existing ones.

With this approach, each `ModelView` is an assembly of smaller, focused views (like `ListModelView`, `CreateModelView`, `RetrieveModelView`, `UpdateModelView`, `DeleteModelView`). You can mix and match these parts to define custom `ModelViewSet` without inheriting from a monolithic base class or overriding its methods. This design increases customization and adaptability across a wide range of use-cases.

# ModelViewSet

`ModelViewSet` is a class that consolidates the **CRUD** operations (**C**reate,**R**etrieve, **U**pdate, and **D**elete) for a Django Model. It's a powerful component that ties together the different views defined in Django Ninja CRUD. This class goes through each of its attributes and registers the routes of those that are instances of `AbstractModelView`.

# AbstractModelView

`AbstractModelView` is an abstract base class that lays the groundwork for other views in Django Ninja CRUD. It defines a standard interface for registering routes for models. Any view that extends `AbstractModelView` must implement the `register_route` method, which adds the view's routes to a given Ninja Router.

# CRUD Views

The actual CRUD operations are implemented in views that extend `AbstractModelView`. These views (e.g., `RetrieveModelView`, `UpdateModelView`, ...) encapsulate the logic for handling specific types of HTTP requests. They define how to **C**reate, **R**etrieve, **U**pdate, and **D**elete instances of Django models.

Each view is designed to be highly _customizable_, with various options and hooks to tailor its behavior. For example, views can be decorated with additional functionality, and you can specify actions to be taken before and after saving an instance during an update or a delete operation.
