#!/bin/bash -x

# Optional login if you are not already logged in
gcloud auth login
gcloud config set project test-seravalli

REGION="europe-west3"
ZONE="${REGION}-a"

# DISK_TYPE=pd-ssd
DISK_TYPE=pd-standard

DISK_NAME="google-${DISK_TYPE}-$(date '+%s')"
gcloud compute disks create ${DISK_NAME} \
  --zone=${ZONE} --type=${DISK_TYPE} --size=500GB

gcloud compute instances create "instance-$(date '+%s')" \
  --zone ${ZONE} --machine-type "n1-standard-1" \
  --disk "name=${DISK_NAME},device-name=${DISK_NAME},mode=rw,boot=no" 

