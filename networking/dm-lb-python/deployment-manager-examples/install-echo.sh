#!/bin/bash -e
ATTR=http://metadata.google.internal/computeMetadata/v1/instance/attributes
apt-get update
apt-get -y install python-pip
pip install --upgrade pip
if pkg=$(curl -sf "${ATTR}/echo" -H "Metadata-Flavor: Google"); then
    pip install --upgrade $pkg
    gunicorn -b 0.0.0.0:80 -w 4 echo:app 
fi

