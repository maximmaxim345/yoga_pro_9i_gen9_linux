#!/usr/bin/env bash

# Function to check if a command exists
command_exists() {
	command -v "$1" >/dev/null 2>&1
}

# Determine whether to use Podman or Docker
if command_exists podman; then
	CONTAINER_ENGINE="podman"
elif command_exists docker; then
	CONTAINER_ENGINE="docker"
else
	echo "Error: Neither Podman nor Docker is installed. Please install one of them and try again."
	exit 1
fi

# Create output directory
mkdir -p ./output

# Build the image
$CONTAINER_ENGINE build -t yoga-icc-builder .

# Run the container
$CONTAINER_ENGINE run -it -v "$(pwd)"/output:/output:z yoga-icc-builder

# Copy the output file to the root of this repo
cp ./output/LEN160_3_2K_cal-linux.icc ../
