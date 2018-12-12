#/bin/zsh -x

for ((i = 0; i < 10; i++)); do
  gcloud compute --project=sandbox-303kdn50 disks create sap-prototype-disk-$(openssl rand -hex 5) --zone=europe-west1-b --type=pd-standard --size=10GB
  sleep 10
done

