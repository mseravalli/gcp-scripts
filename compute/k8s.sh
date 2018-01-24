#!/bin/bash

set -x

# Optional login if you are not already logged in
PROJECT=qwiklabs-gcp-19e67d5ea9051488
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

gcloud container clusters create networklb --num-nodes 3

kubectl run nginx --image=nginx --replicas=3

kubectl expose deployment nginx --port=80 --target-port=80 --type=LoadBalancer

