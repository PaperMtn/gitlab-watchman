# syntax=docker/dockerfile:1

FROM python:3.10
COPY . /opt/gitlab-watchman
WORKDIR /opt/gitlab-watchman
ENV PYTHONPATH=/opt/gitlab-watchman GITLAB_WATCHMAN_TOKEN="" GITLAB_WATCHMAN_URL=""
RUN pip3 install -r requirements.txt build && \
    chmod -R 700 . && \
    python3 -m build && \
    python3 -m pip install dist/*.whl
STOPSIGNAL SIGINT
WORKDIR /opt/gitlab-watchman
ENTRYPOINT ["gitlab-watchman"]