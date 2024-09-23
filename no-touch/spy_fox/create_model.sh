#!/bin/bash

# Define the path to the Modelfile
MODELFILE_PATH="./Modelfile"

# Check if the Modelfile exists
if [ ! -f "$MODELFILE_PATH" ]; then
    echo "Error: Modelfile not found at $MODELFILE_PATH"
    exit 1
fi

# Create the model using ollama
ollama create spy_fox -f "$MODELFILE_PATH"

# Check if the creation was successful
if [ $? -eq 0 ]; then
    echo "Model 'spy_fox' created successfully."
else
    echo "Error: Failed to create the model 'spy_fox'."
    exit 1
fi
