FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy start.sh and give it execute permissions
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port
EXPOSE 5000

# Start the application with the start.sh script
CMD ["/start.sh"]
