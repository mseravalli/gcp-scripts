#!/bin/bash

echo 'Specify --start=1' > lastline

while true
do 
  cat lastline | awk '{print $2}' | xargs -I {} bash -c "gcloud compute --project=test-seravalli instances get-serial-port-output $1 --zone=europe-west3-a {} 2> lastline"
  sleep .5
done
