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
# Description:  Google Cloud Platform - SAP Deployment Functions
# Build Date:   Fri Nov 30 14:59:44 GMT 2018
# ------------------------------------------------------------------------

nfs::create_volume() {
  main::errhandle_log_info 'Building /nfs'
  main::create_vg /dev/sdb vg_nfs
  main::errhandle_log_info "--- Creating logical volume"
  lvcreate -l 100%FREE -n vol1 vg_nfs
  mkdir -p /nfs
}


nfs::config_drbd() {
  main::errhandle_log_info 'Configuring DRBD'
  main::errhandle_log_info '--- creating /etc/drbd.d/nfsvol.res'

  cat <<EOF > /etc/drbd.d/nfsvol.res
  resource nfsvol {
     disk {
        on-io-error detach;
        no-disk-flushes;
        no-disk-barrier;
        c-plan-ahead 0;
        c-fill-target 24M;
        c-min-rate 80M;
        c-max-rate 720M;
     }
     net {
        protocol C;
        max-buffers 8000;
        max-epoch-size 8000;
        sndbuf-size 2M;
        rcvbuf-size 2M;
     }
     connection-mesh {
        hosts ${VM_METADATA[sap_primary_instance]} ${VM_METADATA[sap_secondary_instance]};
     }
     on ${VM_METADATA[sap_primary_instance]} {
        address ${PRIMARY_NODE_IP}:7789;
        device /dev/drbd1 ;
        disk /dev/vg_nfs/vol1;
        meta-disk internal;
        node-id 0;
     }
     on ${VM_METADATA[sap_secondary_instance]} {
        address ${SECONDARY_NODE_IP}:7789;
        device /dev/drbd1 ;
        disk /dev/vg_nfs/vol1;
        meta-disk internal;
        node-id 1;
     }
  }
EOF

  cat <<EOF > /etc/drbd.d/global_common.conf
  global {
     usage-count yes;
     minor-count 5;
     dialog-refresh 1;
  }
  common {
     disk {
     }
     net {
     }
     startup {
     }
     options {
     }
     handlers {
     }
  }
EOF

  cat <<EOF > /etc/drbd.conf
  include "drbd.d/global_common.conf";
  include "drbd.d/*.res";
EOF

  main::errhandle_log_info "--- Creating nfsvol"
  drbdadm create-md nfsvol
  drbdadm up nfsvol
  main::errhandle_log_info "--- Starting DRBD"
  rcdrbd start
  mkdir /nfs
}


nfs::primary_dbrd(){
  rcdrbd start
  sleep 30
  main::errhandle_log_info "--- Setting primary node to master"
  drbdadm primary --force nfsvol
  main::errhandle_log_info "--- Creating filesystem on /dev/drbd1"
  mkfs -t xfs /dev/drbd1
}


nfs::configure_ha_nfs(){
  crm configure primitive drbd_nfs ocf:linbit:drbd params drbd_resource="nfsvol" op monitor interval="15" role="Master" op monitor interval="30" role="Slave"
  crm configure ms ms-drbd_nfs drbd_nfs meta master-max="1" master-node-max="1" clone-max="2" clone-node-max="1" notify="true"
  crm configure primitive nfsserver systemd:nfs-server op monitor interval="30s"
  crm configure clone cl-nfsserver nfsserver
  crm configure primitive rsc_fs_nfs ocf:heartbeat:Filesystem params device=/dev/drbd1 directory=/nfs fstype=xfs op monitor interval="10s"
  crm configure group g-master rsc_fs_nfs
  crm configure order o-drbd_before_nfs inf: ms-drbd_nfs:promote g-master:start
  crm configure colocation col-nfs_on_drbd inf: g-master ms-drbd_nfs:Master
  crm configure delete g-vip
  crm configure modgroup g-master add rsc_vip_int
  crm configure modgroup g-master add rsc_vip_gcp
}
