#!/bin/bash
# ------------------------------------------------------------------------
# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Description:  
# ------------------------------------------------------------------------

PROJECT="sandbox-303kdn50"
NETWORK_NAME="default"
SUBNET="default"
ZONE="europe-west4-c"
TAG="sap-hana"
SID="E36"
VM_NAME="marcosturfdonttuch"
SYS_NR=36
PASSWD="hUk27d.er20"
NEW_INSTANCE_NUMBER=2

# pass desiered state as argument
hana_operations::wait_for_db_operation() {
  # TODO: check that argument is passed
  DESIRED_STATE=$1
  TOTAL_WORKERS=$(gcloud compute ssh ${VM_NAME} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function GetSystemInstanceList'" | grep WORKER | wc -l | sed 's/[ ]*//g')
  READY_WORKERS=$(gcloud compute ssh ${VM_NAME} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function GetSystemInstanceList'" | grep WORKER | grep ${DESIRED_STATE} | wc -l | sed 's/[ ]*//g')
  while [[ $TOTAL_WORKERS != $READY_WORKERS ]]; do
    READY_WORKERS=$(gcloud compute ssh ${VM_NAME} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function GetSystemInstanceList'" | grep WORKER | grep ${DESIRED_STATE} | wc -l | sed 's/[ ]*//g')
    sleep 10
  done
}

hana_operations::stop_db() {
  #sidadm@Master
  gcloud compute ssh ${VM_NAME} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function StopSystem'"
  hana_operations::wait_for_db_operation "GRAY"
}

hana_operations::exportfs() {
  #root@Masrer
  gcloud compute ssh ${VM_NAME} -- "sudo su -c 'echo \"/hana/shared ${VM_NAME}w${NEW_INSTANCE_NUMBER}(rw,no_root_squash,sync,no_subtree_check)\" >> /etc/exports'"
  gcloud compute ssh ${VM_NAME} -- "sudo su -c 'echo \"/hanabackup ${VM_NAME}w${NEW_INSTANCE_NUMBER}(rw,no_root_squash,sync,no_subtree_check)\" >> /etc/exports'"
  gcloud compute ssh ${VM_NAME} -- "sudo su -c 'exportfs -rv'"
}

hana_operations::mount_shared() {
  #root@Worker node 
  gcloud compute ssh ${VM_NAME}w${NEW_INSTANCE_NUMBER} -- "sudo su -c 'mount -av'"
  gcloud compute ssh ${VM_NAME}w${NEW_INSTANCE_NUMBER} -- "sudo su -c 'cd /hana/shared/${SID}/global/hdb/install/bin ; yes | ./hdbremovehost --keep_user_home_dir --keep_user --skip_modify_sudoers --force '"
}

hana_operations::start_db() {
  #sidadm@Master
  gcloud compute ssh ${VM_NAME} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function StartSystem'"
  hana_operations::wait_for_db_operation "GREEN"
}

hana_operations::copy_public_key_to_worker() {
  #root@Master
  ROOT_MASTER_PUB_KEY=$(gcloud compute ssh ${VM_NAME} -- "sudo su -c 'cat ~/.ssh/id_rsa.pub'")

  #root@Worker
  gcloud compute ssh ${VM_NAME}w${NEW_INSTANCE_NUMBER} -- "sudo su -c 'echo ${ROOT_MASTER_PUB_KEY} >> ~/.ssh/authorized_keys'"

  # accept new signature of new worker
  gcloud compute ssh ${VM_NAME} -- "sudo su -c 'ssh -oStrictHostKeyChecking=no ${VM_NAME}w${NEW_INSTANCE_NUMBER} -- exit'"
}


hana_operations::add_node() {
  #root@Master add node 
  TMP_FILE=$(mktemp)
  cat << EOF > ${TMP_FILE}
<?xml version='1.0' encoding='UTF-8'?>
<Passwords>
  <password>
    <![CDATA[${PASSWD}]]>
  </password>
  <sapadm_password>
    <![CDATA[${PASSWD}]]>
  </sapadm_password>
  <system_user_password>
    <![CDATA[${PASSWD}]]>
  </system_user_password>
</Passwords>
EOF

  gcloud compute scp ${TMP_FILE} ${VM_NAME}:/tmp/tmp.tmp 
  gcloud compute ssh ${VM_NAME} -- "chmod 644 /tmp/tmp.tmp"
  gcloud compute ssh ${VM_NAME} -- "sudo su -c 'cat /tmp/tmp.tmp | /hana/shared/${SID}/hdblcm/hdblcm --action=add_hosts --addhosts=${VM_NAME}w${NEW_INSTANCE_NUMBER} --certificates_hostmap=${VM_NAME}w${NEW_INSTANCE_NUMBER}=${VM_NAME}w${NEW_INSTANCE_NUMBER} --root_user=root --listen_interface=global --read_password_from_stdin=xml -b'"
  gcloud compute ssh ${VM_NAME} -- rm -f /tmp/tmp.tmp
  rm -f $TMP_FILE
}

