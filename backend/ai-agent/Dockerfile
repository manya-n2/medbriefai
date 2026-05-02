FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
# FIX: remove problematic fastapi version and install manually
RUN sed -i '/fastapi/d' requirements.txt \
    && pip install --no-cache-dir fastapi uvicorn \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]