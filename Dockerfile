FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY top_file.py .
COPY screenshot.png .
CMD ["python", "top_file.py"]
