#!/bin/zsh -x

# Optional login if you are not already logged in
# gcloud auth login
# gcloud config set project test-seravalli

REGION="europe-west1"
ZONE="${REGION}-c"

gcloud compute instances create "instance-$(date '+%s')" \
  --zone ${ZONE} --machine-type "n1-standard-1" \
  --metadata startup-script="#! /bin/bash
    echo 'set -o vi' >> /root/.bashrc
  "
