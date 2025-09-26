#!/bin/bash

# Define the title (filename) as a variable
target_file="./.github/workflows/run-conventional-commits-check.yml"
source_file="/Users/mcj/code/duchamp/.github/workflows/run-conventional-commits-check.yml"

# Check if the source file exists
if [ ! -f "$source_file" ]; then
    echo "Error: Source file $source_file does not exist."
    exit 1
fi

# Check if the target file exists
if [ ! -f "$target_file" ]; then
    echo "Target file $target_file does not exist. Copying from duchamp..."
    # Create the directory structure if it doesn't exist
    mkdir -p "$(dirname "$target_file")"
    # Copy the file from duchamp
    cp "$source_file" "$target_file"
    echo "File copied successfully."
else
    echo "Target file $target_file exists. Checking for differences..."

    # Compare the files
    if diff -q "$source_file" "$target_file" > /dev/null; then
        echo "Files are identical. No action needed."
    else
        echo "Files are different. Replacing with the version from duchamp..."
        cp "$source_file" "$target_file"
        echo "File replaced successfully."
    fi
fi
