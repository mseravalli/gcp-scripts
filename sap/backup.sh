#!/bin/zsh -x

PROJECT="sandbox-303kdn50"
INSTANCE_NAME="nat-vm"
NETWORK_NAME="default"
SUBNET="default"
ZONE="europe-west4-c"
TAG="sap-hana"
SYS_NR="36"
PASSWD="hUk27d.er20"
VM_NAME="sape36vm"

# gcloud auth login
gcloud config set project $PROJECT

echo "hdbsql -n ${VM_NAME}:3${SYS_NR}15 -u system -p ${PASSWD} \"BACKUP DATA CREATE SNAPSHOT\"" > tmp_cmd.sh
gcloud compute ssh ${VM_NAME} -- "sudo su - e36adm " < tmp_cmd.sh
echo " hdbsql -xaj -n ${VM_NAME}:3${SYS_NR}15 -u system -p ${PASSWD} \"SELECT BACKUP_ID FROM \"PUBLIC\".\"M_BACKUP_CATALOG\" WHERE ENTRY_TYPE_NAME = 'data snapshot' AND STATE_NAME = 'prepared' \" " > tmp_cmd.sh
BACKUP_ID=$(gcloud compute ssh ${VM_NAME} -- " sudo su - e36adm" < tmp_cmd.sh)
echo ${BACKUP_ID}

for ((i=0; i<=2; i++)); do
  WORKER=""
  if [ $i -gt 0 ]; then
    WORKER="w${i}"
  fi
  gcloud compute disks snapshot ${VM_NAME}${WORKER}-pdssd \
    --zone=${ZONE} \
    --snapshot-names=${VM_NAME}${WORKER}-${BACKUP_ID}
done

echo "hdbsql -n ${VM_NAME}:3${SYS_NR}15 -u system -p ${PASSWD} \"BACKUP DATA CLOSE SNAPSHOT BACKUP_ID ${BACKUP_ID} SUCCESSFUL 'gcpstorage'\" " > tmp_cmd.sh
gcloud compute ssh ${VM_NAME} -- "sudo su - e36adm " < tmp_cmd.sh

rm tmp_cmd.sh


