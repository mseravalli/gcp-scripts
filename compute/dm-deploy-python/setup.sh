#!/bin/bash

set -x

# Optional login if you are not already logged in
PROJECT=qwiklabs-gcp-3481d9c854125f89
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

pushd echo
python setup.py sdist
popd

gsutil mb gs://seravalli-test-dm

gsutil -h 'Content-Type: application/gzip' -h 'Cache-Control:private' cp \
  -a public-read echo/dist/echo-0.0.1.tar.gz gs://seravalli-test-dm

gcloud compute firewall-rules create allow-80 \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:80 \
  --source-ranges=0.0.0.0/0

SERVICE_NAME="echo-service-$(date '+%s')"
gcloud deployment-manager deployments create $SERVICE_NAME \
  --config dm/config.yaml

# wait the service to be active
sleep 180

VM_EXTERNAL_IP=$(gcloud compute instances list \
  --filter="name:$SERVICE_NAME" \
  --format='table(EXTERNAL_IP:label="")')

curl -d "Design and Process class ROCKS" -X POST http://$VM_EXTERNAL_IP
