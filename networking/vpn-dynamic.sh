#!/bin/bash

set -x

# Optional login if you are not already logged in
gcloud  auth login
gcloud config set project qwiklabs-gcp-db411b900b8394df

REGION_1="us-east1"
REGION_2="europe-west1"

SUBNET_RANGE_1="10.0.1.0/24"
SUBNET_RANGE_2="10.0.2.0/24"
SUBNET_RANGE_3="10.0.3.0/24"

# Create network 1 and subnet
gcloud compute networks create vpn-network-1 --subnet-mode=custom
gcloud compute networks subnets create subnet-1 \
  --network=vpn-network-1 \
  --region=$REGION_1 \
  --range=$SUBNET_RANGE_1

# Create network 2 and subnet
gcloud compute networks create vpn-network-2 --subnet-mode=custom
gcloud compute networks subnets create subnet-2 \
  --network=vpn-network-2 \
  --region=$REGION_2 \
  --range=$SUBNET_RANGE_2

# Create 1 VM in each subnet
gcloud compute instances create "instance-1" \
  --zone "${REGION_1}-b" \
  --machine-type "n1-standard-1" \
  --subnet "subnet-1"

gcloud compute instances create "instance-2" \
  --zone "${REGION_2}-b" \
  --machine-type "n1-standard-1" \
  --subnet "subnet-2"

# Create firewall rules
gcloud compute firewall-rules create allow-icmp-ssh-network-1 \
  --direction=INGRESS \
  --priority=1000 \
  --network=vpn-network-1 \
  --action=ALLOW \
  --rules=icmp,tcp:22

gcloud compute firewall-rules create allow-icmp-ssh-network-2 \
  --direction=INGRESS \
  --priority=1000 \
  --network=vpn-network-2 \
  --action=ALLOW \
  --rules=icmp,tcp:22

# Create cloud routers
gcloud compute routers create network-1-cr \
  --asn=65470 \
  --network vpn-network-1 \
  --region ${REGION_1}

gcloud compute routers create network-2-cr \
  --asn=65503 \
  --network vpn-network-2 \
  --region ${REGION_2}

# Setup VPN gateway
gcloud compute addresses create vpn-ip-1 --region=${REGION_1}
gcloud compute addresses create vpn-ip-2 --region=${REGION_2}

VPN_IP_1=$(gcloud compute addresses list \
  --filter="name:vpn-ip-1" --format='table(ADDRESS:label="")')
VPN_IP_2=$(gcloud compute addresses list \
  --filter="name:vpn-ip-2" --format='table(ADDRESS:label="")')

# TODO created BGP sessions

gcloud compute target-vpn-gateways create "vpn-1" \
  --region ${REGION_1} --network "vpn-network-1"
gcloud compute forwarding-rules create    "vpn-1-rule-esp" \
  --region ${REGION_1} \
  --address ${VPN_IP_1} \
  --ip-protocol "ESP" \
  --target-vpn-gateway "vpn-1"
gcloud compute forwarding-rules create    "vpn-1-rule-udp500" \
  --region ${REGION_1} \
  --address ${VPN_IP_1} \
  --ip-protocol "UDP" \
  --port-range "500" \
  --target-vpn-gateway "vpn-1"
gcloud compute forwarding-rules create    "vpn-1-rule-udp4500" \
  --region ${REGION_1} \
  --address ${VPN_IP_1} \
  --ip-protocol "UDP" \
  --port-range "4500" \
  --target-vpn-gateway "vpn-1"
gcloud compute vpn-tunnels create "vpn-1-tunnel-2" \
  --region ${REGION_1} \
  --peer-address ${VPN_IP_2} --shared-secret "gcprocks" --ike-version "2" \
  --target-vpn-gateway "vpn-1"

gcloud compute target-vpn-gateways create "vpn-2" \
  --region ${REGION_2} --network "vpn-network-2"
gcloud compute forwarding-rules create "vpn-2-rule-esp" \
  --region ${REGION_2} \
  --address ${VPN_IP_2} \
  --ip-protocol "ESP" \
  --target-vpn-gateway "vpn-2"
gcloud compute forwarding-rules create "vpn-2-rule-udp500" \
  --region ${REGION_2} \
  --address ${VPN_IP_2} \
  --ip-protocol "UDP" \
  --port-range "500" \
  --target-vpn-gateway "vpn-2"
gcloud compute forwarding-rules create "vpn-2-rule-udp4500" \
  --region ${REGION_2} \
  --address ${VPN_IP_2} \
  --ip-protocol "UDP" \
  --port-range "4500" \
  --target-vpn-gateway "vpn-2"
gcloud compute vpn-tunnels create "vpn-2-tunnel-1" \
  --region ${REGION_2} \
  --peer-address ${VPN_IP_2} --shared-secret "gcprocks" --ike-version "2" \
  --target-vpn-gateway "vpn-2"

# Verify connectivity
INSTANCE_1_INTERNAL_IP=$(gcloud compute instances list \
  --filter="name:instance-1" --format='table(INTERNAL_IP:label="")')
INSTANCE_2_INTERNAL_IP=$(gcloud compute instances list \
  --filter="name:instance-2" --format='table(INTERNAL_IP:label="")')
gcloud compute ssh instance-1 \
  --zone "${REGION_1}-b" \
  --command "ping -c 3 $INSTANCE_2_INTERNAL_IP"

# create addional subnet in network 2
gcloud compute networks subnets create subnet-3 \
  --network=vpn-network-2 \
  --region=$REGION_2 \
  --range=$SUBNET_RANGE_3

gcloud compute instances create "instance-3" \
  --zone "${REGION_2}-b" \
  --machine-type "n1-standard-1" \
  --subnet "subnet-3"

# Verify connectivity
INSTANCE_3_INTERNAL_IP=$(gcloud compute instances list \
  --filter="name:instance-3" --format='table(INTERNAL_IP:label="")')
gcloud compute ssh instance-1 \
  --zone "${REGION_1}-b" \
  --command "ping -c 3 $INSTANCE_3_INTERNAL_IP"
