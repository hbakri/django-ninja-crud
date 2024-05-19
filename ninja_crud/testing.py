try:
    from rest_testing import *  # noqa
except ImportError as e:  # pragma: no cover
    raise ImportError(
        """
To use the testing module, you must install the `django-rest-testing` package.

To install it, use one of the following commands:

Using pip:
    $ pip install django-ninja-crud[testing]

Using Poetry:
    $ poetry add django-ninja-crud[testing]

This will install both 'django-ninja-crud' and 'django-rest-testing' packages.
        """
    ) from e
