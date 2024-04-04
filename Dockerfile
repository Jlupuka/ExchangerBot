FROM python:3.11-slim-bullseye
RUN python -m venv /opt/venv
ENV PATH="venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim-bullseye as run-image
COPY --from=compile-image /venv /venv
ENV PATH="venv/bin:$PATH"
WORKDIR /app
COPY . /bot
CMD ["python", "-m", "main"]
