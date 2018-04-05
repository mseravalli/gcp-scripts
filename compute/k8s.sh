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

gcloud container --project "seravalli-test" clusters create "cluster-1" --zone "europe-west1-c" --username "admin" --cluster-version "1.9.2-gke.1" --machine-type "n1-standard-1" --image-type "COS" --disk-size "64" --local-ssd-count "1" --scopes "https://www.googleapis.com/auth/compute","https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --num-nodes "3" --network "default" --enable-cloud-logging --enable-cloud-monitoring --subnetwork "default" --enable-autoupgrade --enable-autorepair

# kubectl run nginx \
#   --image=nginx \
#   --replicas=3
#
# kubectl expose deployment nginx \
#   --port=80 \
#   --target-port=80 \
#   --type=LoadBalancer

