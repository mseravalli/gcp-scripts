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
# Need to define the following variables in order to work
# export PROJECT="sandbox-303kdn50"
# export ZONE="europe-west4-c"
# export SID="E36"
# export SYS_NR=36
# export PASSWD="hUk27d.er20"
# export MASTER="e36-fullsa"
# export NEW_WORKER="e36-fullsaw2"

# pass desiered state as argument
hana_operations::wait_for_db_operation() {
  # TODO: check that argument is passed
  DESIRED_STATE=$1
  TOTAL_WORKERS=$(gcloud compute ssh ${MASTER} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function GetSystemInstanceList'" | grep WORKER | wc -l | sed 's/[ ]*//g')
  READY_WORKERS=$(gcloud compute ssh ${MASTER} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function GetSystemInstanceList'" | grep WORKER | grep ${DESIRED_STATE} | wc -l | sed 's/[ ]*//g')
  while [[ $TOTAL_WORKERS != $READY_WORKERS ]]; do
    READY_WORKERS=$(gcloud compute ssh ${MASTER} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function GetSystemInstanceList'" | grep WORKER | grep ${DESIRED_STATE} | wc -l | sed 's/[ ]*//g')
    sleep 10
  done
}

hana_operations::check_db_status() {
  gcloud compute ssh ${MASTER} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function GetSystemInstanceList'"
}
hana_operations::stop_db() {
  #sidadm@Master
  gcloud compute ssh ${MASTER} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function StopSystem'"
  hana_operations::wait_for_db_operation "GRAY"
  echo "hana stopped"
}

hana_operations::exportfs() {
  #root@Masrer
  gcloud compute ssh ${MASTER} -- "sudo su -c 'echo \"/hana/shared ${NEW_WORKER}(rw,no_root_squash,sync,no_subtree_check)\" >> /etc/exports'"
  gcloud compute ssh ${MASTER} -- "sudo su -c 'echo \"/hanabackup ${NEW_WORKER}(rw,no_root_squash,sync,no_subtree_check)\" >> /etc/exports'"
  gcloud compute ssh ${MASTER} -- "sudo su -c 'exportfs -rv'"
  echo "fs exported"
}

hana_operations::mount_shared() {
  #root@Worker node 
  gcloud compute ssh ${NEW_WORKER} -- "sudo su -c 'mount -av'"
  gcloud compute ssh ${NEW_WORKER} -- "sudo su -c 'cd /hana/shared/${SID}/global/hdb/install/bin ; yes | ./hdbremovehost --keep_user_home_dir --keep_user --skip_modify_sudoers --force '"

  echo "share mounted"
}

hana_operations::start_db() {
  #sidadm@Master
  gcloud compute ssh ${MASTER} -- "sudo su - e36adm -c 'sapcontrol -nr ${SYS_NR} -function StartSystem'"
  hana_operations::wait_for_db_operation "GREEN"

  echo "hana started"
}

hana_operations::copy_public_key_to_worker() {
  #root@Master
  ROOT_MASTER_PUB_KEY=$(gcloud compute ssh ${MASTER} -- "sudo su -c 'cat ~/.ssh/id_rsa.pub'")

  #root@Worker
  gcloud compute ssh ${NEW_WORKER} -- "sudo su -c 'echo ${ROOT_MASTER_PUB_KEY} >> ~/.ssh/authorized_keys'"
 
  # /usr/local/google-cloud-sdk/bin/gcloud --quiet compute instances add-metadata marcosturfdonttuchw1 --metadata 'ssh-keys=root:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDKH+Bl+zphheUmqdssz9//DxY81IDNJPTK2xeiShCdybJ0g5p47YARHciYJJkVlREUZ5RwEy8e/0IT301t+O+P7Lb5JIf1i3D5Yw2zbXOa4eZ6Ksd8+syg9MWMgOqGzLi6bV1Lo9epZo48zIuc+gq90Ae1TPbhxQ8xCDOzGXQhTAqdNOQY72/OXNhtkWN8bygs/n7wf0GB3z8lzD9z91y1xjCcV8grgQIK5P60Ltgk3EXbkdhgsPxXkkJC8ngK8YJTBFcwwnAW/gq2PwCpWIJiC7Nrj+kErpozzIUAZOOuNK7hUSMQu1bLv7SRkdYTsGHJIYo7Hl33xf4G3CrAzeTZ root@marcosturfdonttuch'

  # accept new signature of new worker
  gcloud compute ssh ${MASTER} -- "sudo su -c 'ssh -oStrictHostKeyChecking=no ${NEW_WORKER} -- exit'"

  echo "keys copied"
}


hana_operations::add_node() {
  #root@Master add node 
  TMP_FILE=$(mktemp)
#   cat << EOF > ${TMP_FILE}
# <?xml version="1.0" encoding="UTF-8"?>
# <Passwords>
#   <password>
#     <![CDATA[${PASSWD}]]>
#   </password>
#   <sapadm_password>
#     <![CDATA[${PASSWD}]]>
#   </sapadm_password>
#   <system_user_password>
#     <![CDATA[${PASSWD}]]>
#   </system_user_password>
# </Passwords>
# EOF
  TMP_FILE=$(mktemp)
  cat << EOF > ${TMP_FILE}
<?xml version="1.0" encoding="UTF-8"?><Passwords><password><![CDATA[${PASSWD}]]></password><sapadm_password><![CDATA[${PASSWD}]]></sapadm_password><system_user_password><![CDATA[${PASSWD}]]></system_user_password></Passwords>
EOF

  gcloud compute scp ${TMP_FILE} ${NEW_WORKER}:/tmp/tmp.tmp 
  gcloud compute ssh ${NEW_WORKER} -- "chmod 777 /tmp/tmp.tmp"
  gcloud compute ssh ${NEW_WORKER} -- "sudo su -c 'cat /tmp/tmp.tmp | /hana/shared/${SID}/hdblcm/hdblcm --action=add_hosts --addhosts=${NEW_WORKER} --certificates_hostmap=${NEW_WORKER}=${NEW_WORKER} --root_user=root --listen_interface=global --read_password_from_stdin=xml -b'"
  gcloud compute ssh ${NEW_WORKER} -- rm -f /tmp/tmp.tmp
  rm -f $TMP_FILE
  echo "hana node added"
}


