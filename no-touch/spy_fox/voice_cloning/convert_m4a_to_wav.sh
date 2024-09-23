#!/bin/bash

# Directory containing the .m4a files
input_dir="inputs/"
output_dir="wavs/"

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Loop through each .m4a file in the input directory
for input_file in "$input_dir"/*.m4a; do
    # Extract the filename without the extension
    filename=$(basename "$input_file" .m4a)
    
    # Output file path
    output_file="$output_dir/${filename}.wav"
    
    # Convert to 22050 Hz, 16-bit, mono .wav
    ffmpeg -i "$input_file" -ar 22050 -ac 1 -acodec pcm_s16le "$output_file"
done

echo "Conversion complete!"
