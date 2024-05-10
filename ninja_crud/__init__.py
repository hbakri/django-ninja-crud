from . import views

try:
    import rest_testing as testing

    __all__ = ["views", "testing"]
except ImportError:  # pragma: no cover
    __all__ = ["views"]
