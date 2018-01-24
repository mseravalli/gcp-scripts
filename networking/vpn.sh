#!/bin/bash

# Optional login if you are not already logged in
# gcloud  auth login
# gcloud config set project seravalli-test-190910

set -x

REGION_1="us-east1"
REGION_2="europe-west1"

SUBNET_RANGE_1="10.0.1.0/24"
SUBNET_RANGE_2="10.0.2.0/24"

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

# Set up the VPN for both networks
gcloud compute target-vpn-gateways create vpn-1 \
  --network vpn-network-1  \
  --region $REGION_1

gcloud compute target-vpn-gateways create vpn-2 \
  --network vpn-network-2  \
  --region $REGION_2

# Reserve a static IP for each network
gcloud compute addresses create --region $REGION_1 vpn-1-static-ip
STATIC_IP_VPN_1=$(gcloud compute addresses list \
   --filter="region:$REGION_1" --format='table(address:label="")')
gcloud compute addresses create --region $REGION_2 vpn-2-static-ip
STATIC_IP_VPN_2=$(gcloud compute addresses list \
   --filter="region:$REGION_2" --format='table(address:label="")')

# Create forwarding rules for both vpn gateways
gcloud compute forwarding-rules create vpn-1-esp \
  --region $REGION_1  \
  --ip-protocol ESP  \
  --address $STATIC_IP_VPN_1 \
  --target-vpn-gateway vpn-1

gcloud compute forwarding-rules create vpn-2-esp \
  --region $REGION_2  \
  --ip-protocol ESP  \
  --address $STATIC_IP_VPN_2 \
  --target-vpn-gateway vpn-2

gcloud compute forwarding-rules create vpn-1-udp500  \
  --region $REGION_1 \
  --ip-protocol UDP \
  --ports 500 \
  --address $STATIC_IP_VPN_1 \
  --target-vpn-gateway vpn-1

gcloud compute forwarding-rules create vpn-2-udp500  \
  --region $REGION_2 \
  --ip-protocol UDP \
  --ports 500 \
  --address $STATIC_IP_VPN_2 \
  --target-vpn-gateway vpn-2

gcloud compute forwarding-rules create vpn-1-udp4500  \
  --region $REGION_1 \
  --ip-protocol UDP --ports 4500 \
  --address $STATIC_IP_VPN_1 \
  --target-vpn-gateway vpn-1

gcloud compute forwarding-rules create vpn-2-udp4500  \
  --region $REGION_2 \
  --ip-protocol UDP --ports 4500 \
  --address $STATIC_IP_VPN_2 \
  --target-vpn-gateway vpn-2

# Create tunnels
gcloud compute vpn-tunnels create tunnel1to2  \
  --peer-address $STATIC_IP_VPN_2 \
  --region $REGION_1 \
  --ike-version 2 \
  --shared-secret gcprocks \
  --target-vpn-gateway vpn-1 \
  --local-traffic-selector 0.0.0.0/0 \
  --remote-traffic-selector 0.0.0.0/0

gcloud compute vpn-tunnels create tunnel2to1 \
  --peer-address $STATIC_IP_VPN_1 \
  --region $REGION_2 \
  --ike-version 2 \
  --shared-secret gcprocks \
  --target-vpn-gateway vpn-2 \
  --local-traffic-selector 0.0.0.0/0 \
  --remote-traffic-selector 0.0.0.0/0

# Create static routes
gcloud compute routes create route1to2  \
  --network vpn-network-1 \
  --next-hop-vpn-tunnel tunnel1to2 \
  --next-hop-vpn-tunnel-region $REGION_1 \
  --destination-range $SUBNET_RANGE_2

gcloud compute routes create route2to1  \
  --network vpn-network-2 \
  --next-hop-vpn-tunnel tunnel2to1 \
  --next-hop-vpn-tunnel-region $REGION_2 \
  --destination-range $SUBNET_RANGE_1

# Verify connectivity
INSTANCE_1_INTERNAL_IP=$(gcloud compute instances list \
  --filter="name:instance-1" --format='table(INTERNAL_IP:label="")')
INSTANCE_2_INTERNAL_IP=$(gcloud compute instances list \
  --filter="name:instance-2" --format='table(INTERNAL_IP:label="")')
gcloud compute ssh instance-1 \
  --zone "${REGION_1}-b" \
  --command "ping -c 3 $INSTANCE_2_INTERNAL_IP"

