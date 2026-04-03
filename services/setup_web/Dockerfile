FROM python:3.12-slim

WORKDIR /app
COPY services/setup_web/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/setup_web/app /app/app
COPY scripts/builder_bootstrap.py /app/scripts/builder_bootstrap.py
EXPOSE 3011
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3011"]
