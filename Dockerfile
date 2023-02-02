FROM python:3.9.10

RUN adduser --disabled-password --gecos '' deploy
RUN mkdir -p /src
RUN chown deploy:deploy /src

RUN pip --no-cache-dir install poetry
RUN pip --no-cache-dir install awscli --upgrade

USER deploy
ENV USER deploy
ENV HOME /home/deploy

WORKDIR /src

COPY pyproject.toml /src
RUN poetry install --no-dev

COPY . /src

CMD ["python"]
