#!/bin/bash -xe

############################################################################### 
# Lauch the script using
# $ ./copy-vm-2nics.sh
# 
# The script will
# * Create a VM, attach a disk, format it and store a simple file
# * Configure the VM instance , so that the DISKS are not deleted when the VM
#   is deleted
# * Delete the instance created 
# * Create an additional VPC and subnet
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
  --disk "name=${ATTACHED_DISK_NAME},device-name=${ATTACHED_DISK_NAME},mode=rw,boot=no" \
  --metadata startup-script="#! /bin/bash
      yes | sudo mkfs.ext3 /dev/disk/by-id/${ATTACHED_DISK_NAME}
      sudo mkdir -p /mnt/disks/${ATTACHED_DISK_NAME}
      sudo mount /dev/disk/by-id/${ATTACHED_DISK_NAME} \
        /mnt/disks/${ATTACHED_DISK_NAME}
      sudo chmod 777 -R /mnt/disks/${ATTACHED_DISK_NAME}
      echo 'hello' > /mnt/disks/${ATTACHED_DISK_NAME}/hello.txt
  "

# wait 30 secs for the disk to be formatted and mounted
sleep 30

echo 'original vm created, press enter to continue with deletion'
read

# update vm settings in order not to delete disks
# boot disk has the same name as the instance by default
gcloud compute instances set-disk-auto-delete ${ORIGINAL_VM_NAME} \
  --disk=${ORIGINAL_VM_NAME} \
  --no-auto-delete

# get vm information from the original
CLONED_VM_TYPE=$(gcloud compute instances list --filter="name=( '${ORIGINAL_VM_NAME}' )" --format='table(MACHINE_TYPE:label="")')
CLONED_VM_ZONE=$(gcloud compute instances list --filter="name=( '${ORIGINAL_VM_NAME}' )" --format='table(zone:label="")')
CLONED_VM_ORIGINAL_SUBNET=$(gcloud compute instances list --filter="name=( '${ORIGINAL_VM_NAME}' )" --format=json | jq -r '.[0].networkInterfaces[0].subnetwork' | sed 's/^.*subnetworks\///') 
CLONED_VM_DISKS_NAMES=($(gcloud compute instances list --filter="name=( '${ORIGINAL_VM_NAME}' )" --format=json | jq -r '.[0].disks | map( ( if (.boot) then "" else .source end) )[]' | sed 's/^.*disks\///' ) )
CLONED_VM_DISKS=($(gcloud compute instances list --filter="name=( '${ORIGINAL_VM_NAME}' )" --format=json | jq -r '.[0].disks | map("name="+.source+",device-name="+.deviceName+",mode=rw,boot="+ ( if (.boot) then "yes" else "no" end) )[]' ))

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
CLONED_VM_NAME="instance-$(date '+%s')"

DISKS=""
for d in ${CLONED_VM_DISKS[@]}; do  DISKS="${DISKS} --disk $d " ; done

STARTUP_SCRIPT=""
for d in ${CLONED_VM_DISKS_NAMES[@]}
do
    STARTUP_SCRIPT="${STARTUP_SCRIPT} 
      sudo mkdir -p /mnt/disks/${d} ;
      sudo mount /dev/disk/by-id/${d} /mnt/disks/${d} ;
      sudo chmod 777 -R /mnt/disks/${d} ;
    "
done

gcloud compute instances create ${CLONED_VM_NAME} \
  --zone ${ZONE} --machine-type ${CLONED_VM_TYPE} \
  --network-interface subnet=${CLONED_VM_ORIGINAL_SUBNET} \
  --network-interface subnet=network-1,no-address \
  ${DISKS} \
  --metadata serial-port-enable=1,startup-script="#! /bin/bash
    ${STARTUP_SCRIPT}
  "

echo 'new vm created, press enter to continue with cleanup'
read

# cleanup
gcloud compute instances delete ${CLONED_VM_NAME} \
  --zone ${ZONE} \
  --quiet
gcloud compute disks delete ${ORIGINAL_VM_NAME} \
  --zone=${ZONE} \
  --quiet
gcloud compute disks delete ${ATTACHED_DISK_NAME} \
  --zone=${ZONE} \
  --quiet

gcloud compute networks subnets delete network-1 \
  --region=${REGION} \
  --quiet
gcloud compute networks delete network-1 \
  --quiet

