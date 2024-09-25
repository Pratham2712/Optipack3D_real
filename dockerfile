# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip3 install --upgrade pip setuptools wheel

RUN pip3 install -r requirements.txt

# RUN pip install Django
# RUN pip install sqlparse
# RUN pip install mysqlclient
# RUN pip install pillow
# RUN pip install matplotlib
# RUN pip install pandas
# RUN pip install django-cors-headers

# Copy the application code
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Add entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]