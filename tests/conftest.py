import pytest
from django.apps import apps
from django.conf import settings
from django.test.utils import get_runner


def pytest_configure():
    from tests import test_settings

    settings.configure(default_settings=test_settings)
    apps.populate(settings.INSTALLED_APPS)


@pytest.fixture(scope="session", autouse=True)
def django_db_setup():
    test_runner_cls = get_runner(settings)
    test_runner = test_runner_cls()
    test_runner.setup_databases()
    test_runner.build_suite()
