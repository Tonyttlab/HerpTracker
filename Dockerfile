# HerpTracker Dockerfile - Python Flask with Apache mod_wsgi
FROM python:3.11-slim

# Install Apache and mod_wsgi
RUN apt-get update && apt-get install -y \
    apache2 \
    apache2-dev \
    libapache2-mod-wsgi-py3 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /var/www/herptracker

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p instance app/static/uploads

# Set permissions for www-data user
RUN chown -R www-data:www-data /var/www/herptracker
RUN chmod -R 755 /var/www/herptracker

# Copy Apache configuration
COPY apache.conf /etc/apache2/sites-available/000-default.conf

# Enable required Apache modules
RUN a2enmod wsgi
RUN a2enmod rewrite
RUN a2enmod headers

# Expose port 80
EXPOSE 80

# Set environment variables
ENV PYTHONPATH=/var/www/herptracker
ENV FLASK_APP=wsgi.py

# Start Apache in foreground
CMD ["apache2ctl", "-D", "FOREGROUND"]
