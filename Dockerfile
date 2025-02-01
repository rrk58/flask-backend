FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies for SQL Server ODBC Driver
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    gcc \
    g++ \
    make \
    curl \
    gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Copy application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Start the application
CMD ["python", "app.py"]
