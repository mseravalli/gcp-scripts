#!/bin/bash

LASTLINE=$(mktemp)

echo 'Specify --start=1' > $LASTLINE

while true
do 
  cat $LASTLINE | awk '{print $2}' | xargs -I {} bash -c "gcloud compute instances get-serial-port-output $1 --zone=europe-west4-c {} 2> $LASTLINE"
  sleep .5
done
