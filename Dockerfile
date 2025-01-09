FROM python:3-alpine

WORKDIR /var/lib/font2svg

RUN pip install poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/cache/pypoetry

COPY pyproject.toml poetry.lock .
RUN poetry install

COPY src ./src

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
