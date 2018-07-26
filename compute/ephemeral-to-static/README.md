# README

## Install dependenticies
Ensure your environment has python3.6
```
$ python --version
Python 3.6.5
```
Install the dependencies for the [python client library](https://cloud.google.com/compute/docs/tutorials/python-guide)
and for the flags
```
pip3 install --upgrade google-api-python-client  
pip3 install absl-py
```

## Export [credentials for application](https://cloud.google.com/docs/authentication/getting-started)
Assuming you have stored the credentials in a file called `sa-python.json`.
Export the location of the variable to so that the Python client API can use it.
```
$ export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/sa-python.json
```

## Run by passing the appropriate attributes
```
python3 ephemeral_to_static.py --project_id=test-seravalli-199408 --zone=europe-west3-a
```

