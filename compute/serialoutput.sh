#!/bin/bash

LASTLINE=$(mktemp)
OUTPUT=$(mktemp)

echo 'Specify --start=1' > $LASTLINE

while true
do 
  cat $LASTLINE | awk '{print $2}' | xargs -I {} bash -c "gcloud compute instances get-serial-port-output $1 --zone=europe-west4-c {} 2> $LASTLINE 1> $OUTPUT"

  if [[ $(wc $OUTPUT | awk '{print $1}') -gt 1 ]]; then
    cat $OUTPUT 
  fi

  sleep .5
done
