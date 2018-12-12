#!/bin/zsh
gcloud beta container --project "test-seravalli-199408" clusters \
  create "k8s-certification" --zone "europe-west1-d" --username "admin" \
  --cluster-version "1.9.7-gke.3" --machine-type "n1-standard-1" \
  --image-type "UBUNTU" --disk-type "pd-standard" --disk-size "100" \
  --scopes "https://www.googleapis.com/auth/compute","https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" \
  --num-nodes "3" --enable-cloud-logging --enable-cloud-monitoring \
  --network "default" --subnetwork "default" \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing,KubernetesDashboard \
  --no-enable-autoupgrade --no-enable-autorepair

