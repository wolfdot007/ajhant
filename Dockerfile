FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python -m uvicorn api_agent:app --host 0.0.0.0 --port ${PORT:-8080}"]