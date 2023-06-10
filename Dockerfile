FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install --no-install-recommends -y ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Specify app location
ARG HOME_DIRECTORY=/usr/local/src
ARG APP_DIRECTORY=${HOME_DIRECTORY}/app
WORKDIR $APP_DIRECTORY

# Specify virtual env locations
ENV POETRY_HOME=${HOME_DIRECTORY}/poetry \
    VIRTUAL_ENV=${HOME_DIRECTORY}/venv
ENV PATH="$VIRTUAL_ENV/bin:$POETRY_HOME/bin:$PATH"

# Install poetry
RUN python3 -m venv ${POETRY_HOME} ${VIRTUAL_ENV} && \
    ${POETRY_HOME}/bin/pip install poetry

# Install dependencies
COPY pyproject.toml poetry.lock ${HOME_DIRECTORY}/
RUN poetry install && \
    rm -fr /root/.cache

# Create unpriviledged user
RUN useradd --home-dir $HOME_DIRECTORY --create-home user
USER user

# Copy app
COPY --chown=user . $APP_DIRECTORY

# Run tests
ENV DJANGO_SETTINGS_MODULE=tests.test_settings
CMD ["python", "-m", "django", "test"]
