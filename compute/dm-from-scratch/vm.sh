#!/bin/bash

set -x

# Optional login if you are not already logged in
PROJECT=qwiklabs-gcp-cad82f4f7db6fd65
# gcloud auth login
gcloud config set project $PROJECT

gcloud deployment-manager deployments create "vm-$(date "+%s")" --config vm.yaml
