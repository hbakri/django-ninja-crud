export DJANGO_SETTINGS_MODULE=tests.test_settings

.PHONY: run-tests
run-tests:
	@python -m poetry run coverage run -m django test
	@python -m poetry run coverage report
	@python -m poetry run coverage html
