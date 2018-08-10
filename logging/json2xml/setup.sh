#!/bin/bash -x

gcloud beta functions deploy json2xml \
  --runtime nodejs8 \
  --trigger-http \
  --region europe-west1

