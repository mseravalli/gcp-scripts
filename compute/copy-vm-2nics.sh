#!/bin/bash -xe

############################################################################### 
# Lauch the script using
# $ ./copy-vm-2nics.sh
# 
# The script will
# * Create a VM
# * Configure the VM instance , so that the DISKS are not deleted when the VM
#   is deleted
# * Delete the instance created 
# * Create an additional network and subnet
# * Create a instance with 2 NICs with attached the disks from original VM
# * Bring up the server with 2 NICS with boot disk and data disks mounted
############################################################################### 

# Optional login if you are not already logged in
# gcloud auth login
gcloud config set project test-seravalli-199408

REGION="europe-west3"
ZONE="${REGION}-b"

# DISK_TYPE=pd-ssd
DISK_TYPE=pd-standard

# create the original vm
ATTACHED_DISK_NAME="google-${DISK_TYPE}-$(date '+%s')"
gcloud compute disks create ${ATTACHED_DISK_NAME} \
  --zone=${ZONE} --type=${DISK_TYPE} --size=20GB

ORIGINAL_VM_NAME="instance-$(date '+%s')"
gcloud compute instances create ${ORIGINAL_VM_NAME} \
  --zone ${ZONE} --machine-type "n1-standard-4" \
  --disk "name=${ATTACHED_DISK_NAME},device-name=${ATTACHED_DISK_NAME},mode=rw,boot=no" 

echo 'original vm created, press enter to continue with deletion'
read

# update vm settings in order not to delete disks
# boot disk has the same name as the instance by default
gcloud compute instances set-disk-auto-delete ${ORIGINAL_VM_NAME} \
  --disk=${ORIGINAL_VM_NAME} \
  --no-auto-delete

# delete the vm
gcloud compute instances delete ${ORIGINAL_VM_NAME} \
  --zone ${ZONE} \
  --quiet

echo 'original vm deleted, press enter to continue with creation of new vm'
read

# create secondary network
gcloud compute networks create network-1 \
  --mode=custom

gcloud compute networks subnets create network-1 \
  --network=network-1 \
  --region=${REGION} \
  --range=10.166.0.0/20

# create the new vm
NEW_VM_NAME="instance-$(date '+%s')"
gcloud compute instances create ${NEW_VM_NAME} \
  --zone ${ZONE} --machine-type "n1-standard-4" \
  --network-interface subnet=default,no-address \
  --network-interface subnet=network-1,no-address \
  --disk "name=${ORIGINAL_VM_NAME},device-name=${ORIGINAL_VM_NAME},mode=rw,boot=yes" \
  --disk "name=${ATTACHED_DISK_NAME},device-name=${ATTACHED_DISK_NAME},mode=rw,boot=no" 

echo 'new vm created, press enter to continue with cleanup'
read

# cleanup
gcloud compute instances delete ${NEW_VM_NAME} \
  --zone ${ZONE} \
  --quiet
gcloud compute disks delete ${ATTACHED_DISK_NAME} \
  --zone=${ZONE} \
  --quiet
gcloud compute networks subnets delete network-1 \
  --region=${REGION} \
  --quiet
gcloud compute networks delete network-1 \
  --quiet

