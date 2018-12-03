#!/bin/bash -x

PROJECT=sandbox-303kdn50
# gcloud auth login
gcloud config set project $PROJECT

gcloud services enable deploymentmanager.googleapis.com
gcloud projects add-iam-policy-binding $PROJECT \
  --member serviceAccount:149382556458@cloudservices.gserviceaccount.com \
  --role roles/storage.admin

gcloud projects add-iam-policy-binding $PROJECT \
  --member serviceAccount:149382556458@cloudservices.gserviceaccount.com \
  --role roles/storage.objectAdmin

gcloud projects add-iam-policy-binding $PROJECT \
  --member serviceAccount:149382556458@cloudservices.gserviceaccount.com \
  --role roles/owner

# ensure that the service account has all the necessary permissions
gcloud deployment-manager deployments delete hana-installation --quiet
gcloud deployment-manager deployments create hana-installation \
  --preview \
  --config config.yaml 


