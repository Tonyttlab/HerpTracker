# HerpTracker Dockerfile - Python Flask with Gunicorn
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /var/www/herptracker

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p instance app/static/uploads

# Set permissions
RUN chmod -R 755 /var/www/herptracker
RUN chmod -R 777 instance app/static/uploads

# Expose port 80
EXPOSE 80

# Set environment variables
ENV PYTHONPATH=/var/www/herptracker
ENV FLASK_APP=wsgi.py

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--timeout", "120", "wsgi:application"]
