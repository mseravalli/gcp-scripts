#!/bin/bash -x

PROJECT="sandbox-303kdn50"
INSTANCE_NAME="nat-vm"
NETWORK_NAME="default"
SUBNET="default"
ZONE="europe-west4-c"
TAG="sap-hana"
# gcloud auth login
gcloud config set project $PROJECT

# gcloud services enable deploymentmanager.googleapis.com
# gcloud projects add-iam-policy-binding $PROJECT \
#   --member serviceAccount:149382556458@cloudservices.gserviceaccount.com \
#   --role roles/storage.admin
#
# gcloud projects add-iam-policy-binding $PROJECT \
#   --member serviceAccount:149382556458@cloudservices.gserviceaccount.com \
#   --role roles/storage.objectAdmin
#
# gcloud projects add-iam-policy-binding $PROJECT \
#   --member serviceAccount:149382556458@cloudservices.gserviceaccount.com \
#   --role roles/owner

# gcloud projects add-iam-policy-binding $PROJECT \
#   --member serviceAccount:sa-hana-opeartor@sandbox-303kdn50.iam.gserviceaccount.com \
#   --role roles/owner

# gsutil mb gs://${PROJECT}-saprepo

# NAT installation
# gcloud compute instances create "${INSTANCE_NAME}" --can-ip-forward \
#         --zone "${ZONE}" \
#         --machine-type=n1-standard-8 --subnet "${SUBNET}" \
#         --metadata startup-script="sysctl -w net.ipv4.ip_forward=1; iptables \
#         -t nat -A POSTROUTING -o eth0 -j MASQUERADE" --tags "${TAG}"
#
# gcloud compute routes create nat-route \
#         --network default --destination-range 0.0.0.0/0 \
#         --next-hop-instance ${INSTANCE_NAME} --next-hop-instance-zone ${ZONE} \
#         --tags "${TAG}" --priority 800

# allow ssh connection to hana VMs
# gcloud compute firewall-rules create allow-ssh --network ${NETWORK_NAME} \
#   --allow tcp:22 --source-ranges 0.0.0.0/0 --target-tags "${TAG}"

# gsutil -m rm -r gs://sandbox-303kdn50-deployment-scripts/dm-templates
# gsutil -m cp -R ./dm-templates gs://sandbox-303kdn50-deployment-scripts 

# ensure that the service account has all the necessary permissions
gcloud deployment-manager deployments delete hana-installation --quiet
gcloud deployment-manager deployments create hana-installation --config config.yaml 
  # --preview \

# NAT post installation
# export INSTANCE_NAME="${PROJECT}-hana-vm"
# gcloud compute instances add-tags "$INSTANCE_NAME" --tags="$TAG" --zone=$ZONE
# gcloud compute instances add-tags "$INSTANCE_NAME"w1 --tags="$TAG" --zone=$ZONE
# gcloud compute instances add-tags "$INSTANCE_NAME"w2 --tags="$TAG" --zone=$ZONE
# gcloud compute instances add-tags "$INSTANCE_NAME"w3 --tags="$TAG" --zone=$ZONE
#
# gcloud compute instances delete-access-config "$INSTANCE_NAME" --access-config-name "external-nat" --zone=$ZONE
# gcloud compute instances delete-access-config "$INSTANCE_NAME"w1 --access-config-name "external-nat" --zone=$ZONE
# gcloud compute instances delete-access-config "$INSTANCE_NAME"w2 --access-config-name "external-nat" --zone=$ZONE
# gcloud compute instances delete-access-config "$INSTANCE_NAME"w2 --access-config-name "external-nat" --zone=$ZONE

