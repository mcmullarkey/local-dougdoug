# Command to run your script
# Use an official Python image as a base
FROM python:3.11

# Install system dependencies (including Sox, curl, and necessary build tools)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    sox \
    libsox-fmt-all \
    alsa-utils \
    pulseaudio \
    pulseaudio-utils \
    libsdl2-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Install Ollama for Linux
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy the rest of the application code
WORKDIR /app
RUN git clone https://github.com/ggerganov/whisper.cpp.git
WORKDIR /app/whisper.cpp
RUN make stream
RUN mv ./stream /app/stream
WORKDIR /app
COPY . /app
ENV XDG_RUNTIME_DIR=/app/tmp/xdg_runtime
RUN mkdir -p $XDG_RUNTIME_DIR && chmod 777 $XDG_RUNTIME_DIR

# Upgrade pip and setuptools
RUN pip install --no-cache-dir --upgrade pip setuptools

# Copy requirements and install Python dependencies using pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Create Ollama model
ENV MODELFILE_BASE_PATH="/app/fortune_teller"
RUN chmod +x /app/stream
RUN chmod +x /app/fortune_teller/Modelfile
RUN chmod +x /app/spy_fox/Modelfile
RUN chmod +x /app/pajama_sam/Modelfile

# Expose necessary ports if any services need to be accessed externally
EXPOSE 11434

# Set the default command to run your script
ENTRYPOINT ["python", "run_local_dougdoug.py"]


