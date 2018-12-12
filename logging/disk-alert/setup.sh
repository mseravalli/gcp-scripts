#!/bin/bash -x

gcloud beta functions deploy disk_alert \
  --project sandbox-303kdn50 \
  --runtime nodejs8 \
  --trigger-http \
  --region europe-west1 \
  --env-vars-file env.yaml
  # --set-env-vars GOOGLE_APPLICATION_CREDENTIALS="${PWD}/sa-credentials.json"
