#!/bin/bash

gcloud auth login
gcloud config set project sandbox-303kdn50

gcloud services enable deploymentmanager.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable cloudbilling.googleapis.com
gcloud services enable iam.googleapis.com
gcloud services enable servicemanagement.googleapis.com

# ensure that the service account has all the necessary permissions

gcloud deployment-manager deployments create \
  "deployment-$(openssl rand -base64 6 | awk '{print tolower($0)}')" \
  --config config.yaml 
