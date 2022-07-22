FROM python:3.10
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY Pipfile /app/
COPY Pipfile.lock /app/

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system --deploy
RUN pip install gunicorn

COPY . /app/
