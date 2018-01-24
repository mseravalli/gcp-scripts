#!/bin/bash

set -x

# Optional login if you are not already logged in
# gcloud  auth login
gcloud config set project qwiklabs-gcp-6b3e7f05dde224f2

REGION_1="us-east1"
REGION_2="europe-west1"

ZONE_1="${REGION_1}-b"
ZONE_2="${REGION_2}-b"
ZONE_3="${REGION_2}-c"

SUBNET_RANGE_1="10.0.1.0/24"
SUBNET_RANGE_2="10.0.2.0/24"
SUBNET_RANGE_3="10.0.3.0/24"

# Create vms
for ((i=0; i<3; ++i))
do
  gcloud compute instances create "instance-${i}" \
    --zone $ZONE_1 \
    --machine-type "n1-standard-1" \
    --subnet "default" \
    --metadata "startup-script-url=gs://cloud-training/archinfra/mystartupscript,my-server-id=WebServer-${i}" \
    --scopes "https://www.googleapis.com/auth/cloud-platform" \
    --tags "http-server,network-lb" 
done

gcloud compute firewall-rules create default-allow-http \
  --network=default \
  --action=ALLOW \
  --rules=tcp:80 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server

gcloud compute http-health-checks create "webserver-health" \
  --port "80" \
  --request-path "/" \
  --check-interval "5" \
  --timeout "5" \
  --unhealthy-threshold "2" \
  --healthy-threshold "2"

gcloud compute addresses create ext-ip-1 --region=${REGION_1}
EXTERNAL_IP_1=$(gcloud compute addresses list \
  --filter="name:ext-ip-1" --format='table(ADDRESS:label="")')

gcloud compute target-pools create extloadbalancer \
    --region $REGION_1 --http-health-check webserver-health

for ((i=0; i<3; ++i))
do
  gcloud compute target-pools add-instances extloadbalancer \
  --instances "instance-${i}" \
  --instances-zone=$ZONE_1
done

gcloud compute forwarding-rules create webserver-rule \
    --region $REGION_1 --ports 80 \
    --address $EXTERNAL_IP_1 --target-pool extloadbalancer

for ((i=10; i<13; ++i))
do
  gcloud compute instances create "instance-${i}" \
    --zone $ZONE_2 \
    --machine-type "n1-standard-1" \
    --subnet "default" \
    --metadata "startup-script-url=gs://cloud-training/archinfra/mystartupscript,my-server-id=WebServer-${i}" \
    --scopes "https://www.googleapis.com/auth/cloud-platform" \
    --tags "int-lb" 
done

# create instance groups
gcloud compute instance-groups unmanaged create ig1 \
  --zone $ZONE_1
for ((i=0; i<3; ++i)); do
  gcloud compute instance-groups unmanaged add-instances ig1 \
    --instances=instance-${i} \
    --zone $ZONE_1
done

gcloud compute instance-groups unmanaged create ig2 \
  --zone $ZONE_2
for ((i=10; i<13; ++i)); do
  gcloud compute instance-groups unmanaged add-instances ig2 \
    --instances=instance-${i} \
    --zone $ZONE_2
done

gcloud compute health-checks create tcp my-tcp-health-check \
    --port 80

gcloud compute backend-services create my-int-lb \
    --load-balancing-scheme internal \
    --region $REGION_1 \
    --health-checks my-tcp-health-check \
    --protocol tcp

gcloud compute backend-services add-backend my-int-lb \
  --instance-group ig1 \
  --instance-group-zone $ZONE_1 \
  --region $REGION_1

gcloud compute backend-services create my-int-lb \
    --load-balancing-scheme internal \
    --region $REGION_2 \
    --health-checks my-tcp-health-check \
    --protocol tcp

gcloud compute backend-services add-backend my-int-lb \
  --instance-group ig2 \
  --instance-group-zone $ZONE_2 \
  --region $REGION_2

gcloud compute forwarding-rules create my-int-lb-forwarding-rule \
    --load-balancing-scheme internal \
    --ports 80 \
    --network default \
    --subnet default \
    --region $REGION_1 \
    --backend-service my-int-lb

gcloud compute firewall-rules create allow-internal-lb \
    --network default \
    --source-ranges 10.128.0.0/20 \
    --target-tags int-lb \
    --allow tcp:80,tcp:443

gcloud compute firewall-rules create allow-health-check \
    --network default \
    --source-ranges 130.211.0.0/22,35.191.0.0/16 \
    --target-tags int-lb \
    --allow tcp







