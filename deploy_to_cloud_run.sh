#!/bin/bash

# Set variables
PROJECT_ID="wizz-433619"
SERVICE_NAME="wizz-service"
REGION="europe-west1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Authenticate with Google Cloud
echo "Authenticating with Google Cloud..."
gcloud auth login

# Set the project
echo "Setting the project..."
gcloud config set project $PROJECT_ID

# Enable necessary services
echo "Enabling required Google Cloud services..."
gcloud services enable run.googleapis.com containerregistry.googleapis.com

# Build the Docker image
echo "Building the Docker image..."
gcloud builds submit --tag $IMAGE_NAME .

# Deploy to Google Cloud Run
echo "Deploying the service to Google Cloud Run..."
gcloud run deploy $SERVICE_NAME --image $IMAGE_NAME --platform managed --region $REGION --allow-unauthenticated

# Provide the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
echo "Deployment successful! Your service is live at: $SERVICE_URL"
