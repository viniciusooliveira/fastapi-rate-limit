FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install poetry

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

WORKDIR /app/fastapi_rate_limit

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]


