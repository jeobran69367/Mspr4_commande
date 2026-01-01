FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies after installation to reduce image size
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y gcc g++ libpq-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Expose the correct port for production
EXPOSE 8000

# Update CMD to ensure compatibility with production overrides
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]