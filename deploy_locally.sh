#!/bin/bash

# Set variables
PORT=8080
DOCKER_IMAGE_NAME="wizz-local-service"
CONTAINER_NAME="wizz-local-container"

# Build the Docker image
echo "Building the Docker image..."
sudo docker build -t $DOCKER_IMAGE_NAME .

# Stop and remove any existing container with the same name
echo "Stopping and removing existing container..."
sudo docker stop $CONTAINER_NAME
sudo docker rm $CONTAINER_NAME

# Run the Docker container
echo "Running the Docker container..."
sudo docker run -d -p $PORT:8080 --name $CONTAINER_NAME $DOCKER_IMAGE_NAME

# Wait for a few seconds to ensure the service is up and running
echo "Waiting for the service to start..."
sleep 5

# Open the service in the default web browser
open http://localhost:$PORT
