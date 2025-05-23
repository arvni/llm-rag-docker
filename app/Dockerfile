FROM python:3.11-slim

# Set build arguments
ARG PYTHON_VERSION=3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-spa \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgeos-dev \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/data /app/uploads /app/logs /app/config /app/static \
    && chown -R app:app /app

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app/
RUN chown -R app:app /app

# Switch to app user
USER app

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false", \
     "--server.maxUploadSize=200"]