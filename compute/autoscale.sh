#!/bin/bash

set -x

# Optional login if you are not already logged in
PROJECT=qwiklabs-gcp-af68618fb4684c93
gcloud auth login
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

gcloud compute instances create "webserver-4" \
  --zone $ZONE_3 \
  --machine-type "n1-standard-1" \
  --subnet "default" \
  --tags "http-server","https-server" \
  --boot-disk-type "pd-ssd" \
  --no-boot-disk-auto-delete \
  --boot-disk-device-name "webserver-4" \
  --metadata startup-script='#! /bin/bash
    set -x
    apt-get update
    apt-get install -y apache2
    service apache2 start
    a2ensite default-ssl
    a2enmod ssl
    service apache2 restart
    update-rc.d apache2 enable
  '

sleep 60

gcloud compute instances delete webserver-4 --zone $ZONE_3  -q

gcloud compute firewall-rules create default-allow-http \
  --network=default \
  --action=ALLOW \
  --rules=tcp:80 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=http-server

gcloud compute firewall-rules create default-allow-https \
  --network=default \
  --action=ALLOW \
  --rules=tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=https-server

gcloud compute images create mywebserver1 \
  --source-disk=webserver-4 \
  --source-disk-zone=$ZONE_3

gcloud compute instance-templates create "webserver-template" \
  --machine-type "n1-standard-1" \
  --tags "http-server","https-server" \
  --image "mywebserver1" \
  --image-project $PROJECT \
  --boot-disk-type "pd-ssd" 

gcloud compute http-health-checks create "webserver-healthcheck" \
  --port "80" \
  --request-path "/" \
  --check-interval "5" \
  --timeout "5" \
  --unhealthy-threshold "2" \
  --healthy-threshold "2"

gcloud compute instance-groups managed create "instance-group-1" \
  --region "europe-west1" \
  --base-instance-name "instance-group-1" \
  --template "webserver-template" \
  --size "1"

gcloud compute instance-groups managed set-autoscaling "instance-group-1" \
  --region "europe-west1" \
  --cool-down-period "60" \
  --max-num-replicas "10" \
  --min-num-replicas "1" \
  --target-load-balancing-utilization "0.8"

# TODO find gcloud commands to setup http load balancer 
# atm not provided by the UI
# it's something with forwarding rules

gcloud compute instances create "stress-test" \
  --zone $ZONE_3 \
  --machine-type "n1-standard-1" \
  --boot-disk-type "pd-ssd" \
  --metadata startup-script='#! /bin/bash
    set -x
    apt-get update
    apt-get install -y apache2
  '

# stress test
LB_EXTERNAL_IP=$(gcloud compute forwarding-rules list \
  --format='table(IP_ADDRESS:label="")')
gcloud compute ssh "stress-test" \
  --zone $ZONE_3 \
  --command "ab -n 50000 -c 1000 http://${LB_EXTERNAL_IP}/"

