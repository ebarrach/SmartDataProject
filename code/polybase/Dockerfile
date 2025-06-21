# ----- Base Python Image -----
FROM python:3.11-slim

# ----- System Dependencies -----
RUN apt-get update && apt-get install -y gcc libmariadb-dev

# ----- Working Directory -----
WORKDIR /app

# ----- Copy Application Source -----
COPY . /app

# ----- Install Python Dependencies -----
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ----- Expose Port -----
EXPOSE 8000

# ----- Launch FastAPI with Uvicorn -----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
