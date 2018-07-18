# README

## Install dependenticies
Install the dependencies for the [python client library](https://cloud.google.com/compute/docs/tutorials/python-guide)
and for the flags
```
pip3 install --upgrade google-api-python-client  
pip3 install absl-py
```

## Export [credentials for application](https://cloud.google.com/docs/authentication/getting-started)
```
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/sa-python.json
```

## Run by passing the appropriate attributes
```
python3 consumption.py --project_ids=test-seravalli-199408 --zones=europe-west3-a,europe-west3-b,europe-west3-c
```
