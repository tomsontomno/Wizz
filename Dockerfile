# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app/src

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app/src
COPY . .

# Expose port 8080 to allow external access
EXPOSE 8080

# Run Gunicorn when the container launches with optimized settings
# Only with one worker (this was the main issue with docker cloud deployment)
CMD ["gunicorn", "-w", "1", "--threads", "4", "--timeout", "60", "-b", "0.0.0.0:8080", "--log-level", "debug", "--access-logfile", "-", "--error-logfile", "-", "src.app:app"]
