# Use an official Python image as a base
FROM python:3.11-slim

# Install system dependencies (including Sox, curl, and necessary build tools)
RUN apt-get update && apt-get install -y \
    sox \
    libsox-fmt-all \
    curl \
    git \
    build-essential \
    libffi-dev \
    libssl-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama for Linux
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set environment variables for Pyenv virtual environment compatibility
ENV PYTHONPATH /usr/local/lib/python3.11/site-packages

# Install Python dependencies using pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
WORKDIR /app
COPY . /app

# Expose necessary ports if any services need to be accessed externally
EXPOSE 8000

# Command to run your script
CMD ["python", "run_local_dougdoug.py"]
