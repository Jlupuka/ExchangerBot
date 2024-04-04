FROM python:3.11-slim-bullseye as compile-image
RUN python -m venv /opt/venv
ENV PATH="opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim-bullseye as run-image
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . /bot
CMD ["python", "-m", "/bot/main"]
