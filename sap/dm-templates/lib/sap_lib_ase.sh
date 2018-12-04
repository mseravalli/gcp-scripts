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

ase::create_filesystems() {
  main::errhandle_log_info "Creating file systems for SAP ASE"
  main::create_filesystem /sybase/"${VM_METADATA[sap_ase_sid]}" asesid xfs
  main::create_filesystem /sybase/"${VM_METADATA[sap_ase_sid]}"/sapdata_1 asesapdata xfs
  main::create_filesystem /sybase/"${VM_METADATA[sap_ase_sid]}"/loglog_1 aselog xfs
  main::create_filesystem /sybase/"${VM_METADATA[sap_ase_sid]}"/saptemp asesaptemp xfs
  main::create_filesystem /sybase/"${VM_METADATA[sap_ase_sid]}"/sapdiag asesapdiag xfs
  main::create_filesystem /sybasebackup asebackup xfs
}



