from . import views

try:
    import rest_testing as testing

    __all__ = ["views", "testing"]
except ImportError:
    __all__ = ["views"]
