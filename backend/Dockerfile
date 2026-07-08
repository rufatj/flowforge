# Build from the REPO ROOT context (see docker-compose.yml) so the shared
# eval package ships alongside the app - the backend reuses eval/n8n_client
# and eval/gates instead of duplicating them.
FROM python:3.12-slim

WORKDIR /srv

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app/ and eval/ side by side; app/__init__ finds eval by walking upward.
COPY backend/app ./app
COPY eval ./eval

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
