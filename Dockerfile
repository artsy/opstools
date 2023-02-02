FROM python:3.9.10

RUN adduser --disabled-password --gecos '' deploy
RUN mkdir -p /src
RUN chown deploy:deploy /src

RUN pip --no-cache-dir install poetry
RUN pip --no-cache-dir install awscli --upgrade

WORKDIR /src
COPY pyproject.toml poetry.lock /src/
RUN poetry config virtualenvs.create false \
  && poetry install --without dev

USER deploy
ENV USER deploy
ENV HOME /home/deploy

COPY . /src

CMD ["python"]
