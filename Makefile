.PHONY: build
build:
	@docker build -t django-ninja-crud .

.PHONY: run-tests
run-tests:
	@docker run --rm django-ninja-crud
