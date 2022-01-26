FROM python:3.8

RUN pip --no-cache-dir install poetry
RUN pip --no-cache-dir install awscli --upgrade

WORKDIR /src
COPY . /src
RUN poetry install

CMD ["python"]
