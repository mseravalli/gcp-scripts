#!POWERSHELL
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

### - main functions
function main-errhandle_log_info($message) {
  gcloud logging write $env:computername.ToLower() "$env:computername Deployment '$message'" --severity=INFO 2> $null
}


function main-errhandle_log_warning($message) {
  gcloud logging write $env:computername.ToLower() "$env:computername Deployment '$message'" --severity=WARNING 2> $null
}


function main-errhandle_log_error($message) {
  gcloud logging write $env:computername.ToLower() "$env:computername Deployment '$message'" --severity=ERROR 2> $null
}


function main-create_volume([uInt32]$disk,[string]$letter,[string]$label) {
  main-errhandle_log_info "--- Creating ${letter}:\ (${label})"
  Get-Disk |
  Where number -eq $disk |
  Initialize-Disk -PartitionStyle GPT -PassThru |
  New-Partition -DriveLetter $letter -UseMaximumSize |
  Format-Volume -FileSystem NTFS -NewFileSystemLabel "$label" -Confirm:$false
}


function main-update_registry(){
  main-errhandle_log_info "Updating registry settings"
  $registryPath = "HKLM:\System\CurrentControlSet\Services\LanmanWorkStation\Parameters"
  New-ItemProperty -Path $registryPath -Name DisableCARetryOnInitialConnect -Value 1 -PropertyType DWORD -Force | Out-Null
}


### - gcp functions
function gcp-create_static_ip() {
  $webclient = (New-Object Net.WebClient)
  $webclient.Headers.Add("Metadata-Flavor", "Google")
  $GCP_IP = $webclient.DownloadString("http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/ip")
  $GCP_ZONE = $webclient.DownloadString("http://metadata.google.internal/computeMetadata/v1/instance/zone")
  $GCP_ZONE = ($GCP_ZONE -split '/')[-1]
  $GCP_REGION = $GCP_ZONE.Substring(0, $GCP_ZONE.lastIndexOf('-'))
  $GCP_SUBNET = gcloud compute instances describe $env:COMPUTERNAME.ToLower() --zone $GCP_ZONE | Select-String -Pattern "subnetwork:"
  $GCP_SUBNET = ($GCP_SUBNET -split '/')[-1]
	main-errhandle_log_info "Creating static IP address ${GCP_IP} in subnetwork $GCP_SUBNET"
  gcloud compute addresses create $env:computername.ToLower() --addresses $GCP_IP --region $GCP_REGION --subnet $GCP_SUBNET
}


function gcp-remove_metadata($key) {
  $webclient = (New-Object Net.WebClient)
  $webclient.Headers.Add("Metadata-Flavor", "Google")
  $GCP_ZONE = $webclient.DownloadString("http://metadata.google.internal/computeMetadata/v1/instance/zone")
  $GCP_ZONE = ($GCP_ZONE -split '/')[-1]
  main-errhandle_log_info "Removing metadata $key"
	gcloud compute instances remove-metadata $env:computername.ToLower() --zone $GCP_ZONE --keys $key | Out-Null
}


### - NetWeaver functions
function nw-create_pagefile() {
  If ((Test-Path -Path "P:")) {
    $drive = Get-WmiObject Win32_LogicalDisk -filter "deviceid='P:'" -ComputerName $env:COMPUTERNAME
    $swapsize =[int]($drive.FreeSpace/1MB-256)
    main-errhandle_log_info "Creating pagefile P:\pagefile.sys ($swapsize MB)"
    Set-WmiInstance -Class Win32_PageFileSetting -Arguments @{name="P:\pagefile.sys"; InitialSize = $swapsize; MaximumSize = $swapsize} `
    -EnableAllPrivileges |Out-Null
  }
}


main-errhandle_log_info "INSTANCE DEPLOYMENT STARTING"
gcp-remove_metadata windows-startup-script-url
gcp-create_static_ip
main-update_registry
main-errhandle_log_info "Creating file systems for SAP ASE"
main-create_volume 1 D "ASE"
main-create_volume 2 T "ASE Temp"
main-create_volume 3 L "ASE Log"
main-create_volume 4 E "ASE Data"
main-create_volume 5 X "Backup"
main-create_volume 6 S "SAP"
main-create_volume 7 P "Pagefile"
nw-create_pagefile
main-errhandle_log_info "INSTANCE DEPLOYMENT COMPLETE"
