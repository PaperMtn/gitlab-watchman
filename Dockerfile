FROM alpine/git AS initlayer
WORKDIR /workdir
RUN git clone https://github.com/PaperMtn/gitlab-watchman.git

FROM python:buster
RUN addgroup --gid 1000 gitlab-watchman
RUN useradd -u 1000 -g 1000 gitlab-watchman
RUN mkdir /home/gitlab-watchman
COPY --from=initlayer /workdir/gitlab-watchman /home/gitlab-watchman
RUN chown -R gitlab-watchman: /home/gitlab-watchman
WORKDIR /home/gitlab-watchman

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install requests build PyYAML
RUN python3 -m build
RUN python3 -m pip install dist/*.whl

USER gitlab-watchman

ENTRYPOINT ["/usr/local/bin/gitlab-watchman"]