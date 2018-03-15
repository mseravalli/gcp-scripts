#!/bin/bash -x

# Optional login if you are not already logged in
PROJECT=seravalli-test
# gcloud auth login
gcloud config set project $PROJECT

REGION_1="us-east1"
REGION_2="europe-west1"

ZONE_1="${REGION_1}-b"
ZONE_2="${REGION_1}-c"
ZONE_3="${REGION_2}-b"
ZONE_4="${REGION_2}-c"

SUBNET_RANGE_1="10.0.1.0/24"
SUBNET_RANGE_2="10.0.2.0/24"
SUBNET_RANGE_3="10.0.3.0/24"
SUBNET_RANGE_4="10.0.3.0/24"

# set static ip address within network
gcloud compute addresses create "static-ip" \
    --region $REGION_1 --subnet default # --addresses 10.156.0.16

gcloud compute instances create static-ip-$(date '+%s') \
    --private-network-ip static-ip \
    --zone $ZONE_1
    --subnet default





