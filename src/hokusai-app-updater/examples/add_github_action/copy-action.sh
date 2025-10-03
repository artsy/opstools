#!/bin/bash

CODE_DIR_ROOT="$1"
PROJECT="$2"
FILENAME="$3"

# Check for required arguments
if [ -z "$CODE_DIR_ROOT" ] || [ -z "$PROJECT" ] || [ -z "$FILENAME" ]; then
    echo "Usage: $0 <src_root> <project> <filename>"
    exit 1
fi

SOURCE="${CODE_DIR_ROOT}/duchamp/templates/$FILENAME"
TARGET="${CODE_DIR_ROOT}/${PROJECT}/.github/workflows/$FILENAME"

# Check if the source file exists
if [ ! -f "$SOURCE" ]; then
    echo "Error: Source file $SOURCE does not exist."
    exit 1
fi

# Check if the target file exists
if [ ! -f "$TARGET" ]; then
    echo "Target file $TARGET does not exist. Copying from duchamp..."
    # Create the directory structure if it doesn't exist
    mkdir -p "$(dirname "$TARGET")"
    # Copy the file from duchamp
    cp "$SOURCE" "$TARGET"
    # track file in git
    git add -N "$TARGET"

    echo "File copied successfully."
else
    echo "Target file $TARGET exists. Checking for differences..."

    # Compare the files
    if diff -q "$SOURCE" "$TARGET" > /dev/null; then
        echo "Files are identical. No action needed."
    else
        echo "Files are different. Replacing with the version from duchamp..."
        cp "$SOURCE" "$TARGET"
        echo "File replaced successfully."
    fi
fi
