#!/bin/bash

set -x

REGION_1="us-east1"
REGION_2="europe-west1"

gcloud compute routes delete route2to1 --quiet
gcloud compute routes delete route1to2 --quiet

gcloud compute vpn-tunnels delete tunnel2to1 --quiet --region $REGION_2
gcloud compute vpn-tunnels delete tunnel1to2 --quiet --region $REGION_1

gcloud compute forwarding-rules delete vpn-2-udp4500 --quiet --region $REGION_2 
gcloud compute forwarding-rules delete vpn-1-udp4500 --quiet --region $REGION_1

gcloud compute forwarding-rules delete vpn-1-udp500  --quiet --region $REGION_1 
gcloud compute forwarding-rules delete vpn-2-udp500  --quiet --region $REGION_2 

gcloud compute forwarding-rules delete vpn-1-esp --quiet --region $REGION_1 
gcloud compute forwarding-rules delete vpn-2-esp --quiet --region $REGION_2

gcloud compute addresses delete vpn-1-static-ip --quiet --region $REGION_1
gcloud compute addresses delete vpn-2-static-ip --quiet --region $REGION_2

gcloud compute target-vpn-gateways delete vpn-1 --quiet --region $REGION_1
gcloud compute target-vpn-gateways delete vpn-2 --quiet --region $REGION_2

gcloud compute instances delete instance-1 --quiet --zone "${REGION_1}-b"
gcloud compute instances delete instance-2 --quiet --zone "${REGION_2}-b"

gcloud compute firewall-rules delete allow-icmp-ssh-network-1 --quiet
gcloud compute firewall-rules delete allow-icmp-ssh-network-2 --quiet

gcloud compute networks subnets delete subnet-1 --quiet --region $REGION_1
gcloud compute networks subnets delete subnet-2 --quiet --region $REGION_2

gcloud compute networks delete vpn-network-1 --quiet 
gcloud compute networks delete vpn-network-2 --quiet
