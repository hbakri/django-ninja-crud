# The Django Ninja CRUD Documentation

![Django Ninja CRUD Cover](https://raw.githubusercontent.com/hbakri/django-ninja-crud/main/docs/assets/images/django-ninja-crud-cover.JPG)

**Django Ninja CRUD** introduces [**modularity**](https://en.wikipedia.org/wiki/Modular_programming) to API development with [**Django Ninja**](https://github.com/vitalik/django-ninja), revolutionizing how APIs are built and maintained at scale while avoiding repetition. It empowers developers to create reusable, [**composable**](https://en.wikipedia.org/wiki/Composability) API views ranging from built-in [**CRUD** (**C**reate, **R**ead, **U**pdate, **D**elete)](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations to complex custom endpoints, supporting both sync and async implementations, all with minimal boilerplate code.

## 🌞 Key Features
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

## 🫶 Support
First and foremost, a heartfelt thank you to the 400+ stargazers who have shown their
support for this project!

[![Star History Chart](https://api.star-history.com/svg?repos=hbakri/django-ninja-crud&type=Date)](https://star-history.com/#hbakri/django-ninja-crud&Date)

As an open-source project, Django Ninja CRUD thrives on community contributions and
support. Here are some ways you can help:

- 🌟 Star the repo
- 🙌 Share your experience
- 🐝 Report issues
- 🔥 Contribute code
- 💕 [Sponsor the project](https://github.com/sponsors/hbakri)

Your support, in any form, propels this project forward and helps it reach more
developers in need of a powerful, intuitive API development framework. Thank you! 🙏
