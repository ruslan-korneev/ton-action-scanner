FROM python:3.12.7-slim-bullseye

COPY --from=ghcr.io/astral-sh/uv:0.5.29 /uv /uvx /bin/
COPY . /app

WORKDIR /app
RUN uv pip install -r pyproject.toml --system --no-cache

ENTRYPOINT ["scripts/entrypoint.sh"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
