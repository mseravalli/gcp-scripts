#!/bin/bash -xe

# sudo mkfs.ext4 -m 0 -F -E lazy_itable_init=0,lazy_journal_init=0,discard \
#  /dev/disk/by-id/google-persistent-disk

yes | sudo mkfs.ext3 /dev/disk/by-id/google-persistent-disk

sudo mkdir -p /mnt/disks/google-persistent-disk

sudo mount /dev/disk/by-id/google-persistent-disk \
  /mnt/disks/google-persistent-disk

sudo chmod 777 -R /mnt/disks/google-persistent-disk
