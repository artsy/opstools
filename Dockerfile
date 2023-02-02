FROM python:3.9.10

RUN pip --no-cache-dir install poetry
RUN pip --no-cache-dir install awscli --upgrade

WORKDIR /src
COPY . /src
RUN poetry install --no-dev

CMD ["python"]
