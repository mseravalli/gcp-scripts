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

## Check to see if a custom script path was provieded by the template
if [[ "${1}" ]]; then
  readonly DEPLOY_URL="${1}"
else
  readonly DEPLOY_URL="https://storage.googleapis.com/sapdeploy/dm-templates"
fi

## Import includes
source /dev/stdin <<< "$(curl -s ${DEPLOY_URL}/lib/sap_lib_main.sh)"
source /dev/stdin <<< "$(curl -s ${DEPLOY_URL}/lib/sap_lib_ha.sh)"
source /dev/stdin <<< "$(curl -s ${DEPLOY_URL}/lib/sap_lib_nfs.sh)"

### Base GCP and OS Configuration
main::get_os_version
main::install_gsdk /usr/local
main::install_packages
main::config_ssh
main::get_settings
main::create_static_ip
ha::check_settings

## Disk Setup
nfs::create_volume
nfs::config_drbd
nfs::primary_dbrd

## Setup HA
ha::install_secondary_sshkeys
ha::download_scripts
ha::config_pacemaker_primary
ha::ready
ha::check_cluster
ha::pacemaker_add_vip
ha::pacemaker_add_stonith
ha::pacemaker_config_bootstrap_nfs

## add NFS to HA Setup
nfs::configure_ha_nfs

## close out
main::complete
