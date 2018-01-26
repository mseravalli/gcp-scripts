#!/bin/bash

set -x

# Optional login if you are not already logged in
PROJECT=qwiklabs-gcp-9975b14345475c86
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

gsutil cp gs://cloud-training/archdp/archdp-echo.tar.gz .

tar -xzvf archdp-echo.tar.gz

cp http-lb.yaml deployment-manager-examples/
cp http-lb-service.jinja deployment-manager-examples/
cp http-lb-service.jinja.schema deployment-manager-examples/

pushd echo
python setup.py sdist
popd

gsutil mb gs://seravalli-test-deploy

gsutil -h 'Content-Type: application/gzip' -h 'Cache-Control:private' cp \
  -a public-read echo/dist/echo-0.0.1.tar.gz gs://seravalli-test-deploy

gcloud compute firewall-rules create "allow-healthchecks" \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp \
  --source-ranges="130.211.0.0/22,35.191.0.0/16"

SERVICE_NAME="echo-service-$(date '+%s')"
gcloud deployment-manager deployments create $SERVICE_NAME \
  --config deployment-manager-examples/http-lb.yaml

# wait the service to be active
sleep 240

EXTERNAL_IP=$(gcloud compute forwarding-rules list \
  --filter="name:$SERVICE_NAME" \
  --format='table(IP_ADDRESS:label="")')

curl -d "Design and Process class ROCKS" -X POST http://$EXTERNAL_IP

gsutil rm -r gs://seravalli-test-deploy
