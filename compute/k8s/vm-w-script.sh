#!/bin/zsh -x

# Optional login if you are not already logged in
# gcloud auth login
# gcloud config set project test-seravalli

REGION="europe-west1"
ZONE="${REGION}-c"

gcloud compute instances create "instance-$(date '+%s')" \
  --zone ${ZONE} --machine-type "n1-standard-1" \
  --image=ubuntu-1804-bionic-v20180717b --image-project=ubuntu-os-cloud \
  --metadata startup-script="#! /bin/bash
    echo 'set -o vi' >> /root/.bashrc
    update-alternatives --set editor /usr/bin/vim.basic
    apt-get -y install \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    apt-key fingerprint 0EBFCD88
    add-apt-repository \
       'deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable'
    echo 'deb http://apt.kubernetes.io/ kubernetes-xenial main' > /etc/apt/sources.list.d/kubernetes.list
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

    apt-get update
    apt-get -y install docker-ce

  "
