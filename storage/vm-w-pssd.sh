#!/bin/bash

# Optional login if you are not already logged in
gcloud auth login
gcloud config set seravalli-test

set -x

REGION="us-east1"
ZONE="${REGION}-b"

gcloud compute disks create google-local-ssd-0 \
  --zone=${ZONE} --type=pd-ssd --size=500GB

gcloud compute instances create "instance-%(date '+%s')" \
  --zone ${ZONE} --machine-type "n1-standard-16" \
  --disk "name=google-local-ssd-0,device-name=google-local-ssd-0,mode=rw,boot=no" 

