#!/bin/bash

# Use the environment variable MODELFILE_BASE_PATH or fallback to the current directory
MODELFILE_PATH="${MODELFILE_BASE_PATH:-$(pwd)}/Modelfile"

# Check if the Modelfile exists
if [ ! -f "$MODELFILE_PATH" ]; then
    echo "Error: Modelfile not found at $MODELFILE_PATH"
    exit 1
fi

# Create the model using ollama
ollama create fortune_teller -f "$MODELFILE_PATH"

# Check if the creation was successful
if [ $? -eq 0 ]; then
    echo "Model 'fortune_teller' created successfully."
else
    echo "Error: Failed to create the model 'fortune_teller'."
    exit 1
fi
