# Use official Python runtime as base image
FROM python:3.10-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1 
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PATH="/root/.local/bin:${PATH}"

# Set work directory in container
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apk update && apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    mariadb-dev \
    musl-dev \
    libffi-dev \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN groupadd -r django && useradd -r -g django django
USER django

# Copy requirements file
COPY requirements.txt .

RUN pip install mysqlclient
# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code to container
COPY . .

# Collect static files (if using Django's static files)
RUN mkdir -p /app/staticfiles
RUN python manage.py collectstatic --noinput --clear || true

# Expose the port Django runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "messaging_app.wsgi:application"]