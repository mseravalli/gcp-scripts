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

db2::fix_services() {
  main::errhandle_log_info "Updating /etc/services"
  grep -v '5912/tcp\|5912/udp\|5912/stcp' /etc/services > /etc/services.new
  cp /etc/services /etc/services.bak
  mv /etc/services.new /etc/services
}


db2::create_filesystems() {
  main::errhandle_log_info "Creating file systems for IBM DB2"
  main::create_filesystem /db2/"${VM_METADATA[sap_ibm_db2_sid]}" db2sid xfs
  main::create_filesystem /db2/"${VM_METADATA[sap_ibm_db2_sid]}"/db2dump db2dump xfs
  main::create_filesystem /db2/"${VM_METADATA[sap_ibm_db2_sid]}"/sapdata db2sapdata xfs
  main::create_filesystem /db2/"${VM_METADATA[sap_ibm_db2_sid]}"/saptmp db2saptmp xfs
  main::create_filesystem /db2/"${VM_METADATA[sap_ibm_db2_sid]}"/log_dir db2log xfs
  main::create_filesystem /db2/db2"${VM_METADATA[sap_ibm_db2_sid],,}" db2home xfs
  main::create_filesystem /db2backup db2backup xfs
}
