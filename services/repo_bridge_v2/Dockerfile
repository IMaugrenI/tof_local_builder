FROM python:3.12-slim

WORKDIR /app
COPY services/repo_bridge_v2/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY services/repo_bridge_v2/app /app/app
EXPOSE 8099
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8099"]
