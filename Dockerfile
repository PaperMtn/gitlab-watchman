# syntax=docker/dockerfile:1
FROM python:3.12-slim-bullseye AS builder
WORKDIR /opt/gitlab-watchman
COPY . .
RUN pip install poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev && \
    poetry build

FROM python:3.12-slim-bullseye
WORKDIR /opt/gitlab-watchman
COPY --from=builder /opt/gitlab-watchman/dist/*.whl /opt/gitlab-watchman/dist/
COPY --from=builder /opt/gitlab-watchman/pyproject.toml /opt/gitlab-watchman/poetry.lock /opt/gitlab-watchman/
ENV PYTHONPATH=/opt/gitlab-watchman \
    GITLAB_WATCHMAN_TOKEN="" \
    GITLAB_WATCHMAN_URL=""
RUN pip install dist/*.whl && \
    chmod -R 700 .
STOPSIGNAL SIGINT
ENTRYPOINT ["gitlab-watchman"]